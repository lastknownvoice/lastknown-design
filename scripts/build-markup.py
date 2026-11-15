#!/usr/bin/env python3
"""Generate the lastknown.design one-pager.

The mark is **Huxley** — the 24x24 cellular canvas: X-shaped eyes, a
neutral mouth, and a heart at the chest that beats.

The colourway is taken from *A to Z of The Designers Republic* (Thames &
Hudson): an orange ground, a near-black graphic, a hot pink accent and
a pale peach for text.

Geometry and motion are lifted from the Huxley source so the mark is the
same character, not a redraw:

  - shape     -> dev/huxley/huxley-24.js (the heart's cell offsets)
  - timing    -> dev/huxley/huxley-24.js (the lub-dub heartbeat)
  - palette   -> sampled from the Designers Republic cover

The mark is drawn in CSS grid, so the page stays a single static file
with no canvas and no runtime.

The heartbeat is not a blink. Each cell animates its own opacity on a
delay set by its distance from the heart's centre, so the pulse travels
outward through the shape as a ripple -- the heart reads as alive rather
than as a shape that switches on and off. Huxley's lub-dub survives as
the envelope: a full crest, a dimmer second crest, then rest.

Run:  python3 scripts/build-markup.py
Out:  index.html
"""

import math
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
HUXLEY = pathlib.Path("/Users/ianroberts/dev/huxley/huxley-24.js")

# --------------------------------------------------------------------------
# The Designers Republic colourway, sampled from the book cover
# --------------------------------------------------------------------------

PALETTE = {
    "ground": "#FFA918",   # the orange field
    "ink": "#2F414D",      # the near-black graphic
    "pink": "#FD447E",     # the hot pink accent
    "pale": "#EFD8C9",     # the pale peach used for text
}

# Dark mode: the same four, re-grounded on ink rather than orange.
PALETTE_DARK = {
    "ground": "#1B262E",
    "ink": "#F2A919",
    "pink": "#FF6E9C",
    "pale": "#F5E3D8",
}


# --------------------------------------------------------------------------
# Read the character out of the Huxley source
# --------------------------------------------------------------------------

def load_heart():
    """The heart's cell offsets, relative to its centre."""
    source = HUXLEY.read_text(encoding="utf-8")
    block = re.search(r"const HEART_SHAPE\s*=\s*\[(.*?)\];", source, re.S)
    if not block:
        raise SystemExit("could not find HEART_SHAPE in huxley-24.js")
    offsets = re.findall(r"\[\s*(-?\d+)\s*,\s*(-?\d+)\s*\]", block.group(1))
    return [(int(x), int(y)) for x, y in offsets]


HEART = load_heart()

# Huxley puts the heart at the chest of a 24x24 grid. The mark is the
# heart alone, so the grid closes in around it: the heart's own 5x5
# footprint becomes the canvas, and the cells get bigger to keep the
# mark's presence on the page.
GRID = 5
HEART_CX = 2
HEART_CY = 2

# The wave: a ripple travelling out from the heart's centre.
#
# Delay is set per cell by its radius from the centre, so the pulse
# crosses the shape as a moving ring instead of the whole heart
# flashing at once. Cells are grouped into rings by radius and each
# ring is one step further out than the last, so the wave reads as
# discrete rings travelling rather than a uniform blur.
#
# The heart's centre cell is the origin, and it stays dimmer at the
# crest -- as it does in Huxley -- so the ripple has a soft core and
# the shape keeps a focal point.
WAVE_STEP_MS = 35
CYCLE = "2.2s"
BASE_OPACITY = 0.16
CENTER_PEAK = 0.45


def wave_rings():
    """The heart's distinct radii from the centre, ranked outward."""
    radii = sorted({round(math.hypot(lx, ly), 4) for lx, ly in HEART})
    return {radius: rank for rank, radius in enumerate(radii)}


RINGS = wave_rings()


def heart_cells():
    """The heart as (col, row) pairs on the 5x5 grid."""
    return [(HEART_CX + lx, HEART_CY + ly) for lx, ly in HEART]


# --------------------------------------------------------------------------
# Markup
# --------------------------------------------------------------------------

def cell(col, row, cls, extra=""):
    """One grid cell as a div, positioned with the CSS grid."""
    # `extra` is appended as further declarations, so it needs its own
    # leading semicolon.
    suffix = f";{extra}" if extra else ""
    return (
        f'<i class="c {cls}" style="grid-area:{row + 1}/{col + 1};'
        f'{suffix.lstrip(";")}"></i>'
    )


def mark_cells():
    """The heart alone, each cell carrying its place in the wave."""
    out = []
    for (lx, ly), (col, row) in zip(HEART, heart_cells()):
        # The centre cell of the heart is the focal point and stays
        # dimmer, as it does in Huxley.
        is_center = (lx == 0 and ly == 0)
        peak = CENTER_PEAK if is_center else 1.0
        # The delay has to carry its unit -- a bare number is not a valid
        # <time>, and `animation-delay` would silently fall back to 0s,
        # which collapses the whole wave into a single blink.
        delay = RINGS[round(math.hypot(lx, ly), 4)] * WAVE_STEP_MS
        out.append(
            cell(
                col,
                row,
                "heart",
                extra=(
                    f"--d:{delay}ms;--peak:{peak};"
                    f"--half:{peak * 0.5};--base:{BASE_OPACITY}"
                ),
            )
        )
    return "\n        ".join(out)


def favicon_markup():
    """A still heart for the favicon — the mark's focal point.

    At 16px the heart is the only thing that reads, and it is the part
    that carries the beat.
    """
    cells = []
    for col, row in heart_cells():
        # A 64x64 box with a 5x5 grid of 10px cells plus 2px gutters.
        x = col * 12 + 2
        y = row * 12 + 2
        cells.append(f'<rect x="{x}" y="{y}" width="10" height="10" fill="{PALETTE["pink"]}"/>')
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
        + "".join(cells)
        + "</svg>"
    )


def favicon_uri():
    svg = favicon_markup()
    return (
        "data:image/svg+xml,"
        + svg.replace("<", "%3C").replace(">", "%3E").replace('"', "%22").replace("#", "%23")
    )


HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Last Known Design</title>
<meta name="description" content="Last Known Design — a practice and a body of work on how AI agents should behave.">
<meta property="og:title" content="lastknown.design">
<meta property="og:description" content="Last Known Design — a practice and a body of work on how AI agents should behave.">
<meta property="og:type" content="website">
<meta name="theme-color" content="#FFA918" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#1B262E" media="(prefers-color-scheme: dark)">
<link rel="canonical" href="https://lastknown.design/">
<link rel="icon" href="__FAVICON__">

<style>
  :root {
    --ground:  __GROUND__;
    --ink:     __INK__;
    --pink:    __PINK__;
    --pale:    __PALE__;

    --cell:    clamp(11px, 3.2vw, 17px);
    --gap:     clamp(3px, .9vw, 5px);

    --serif: "Iowan Old Style", "Palatino Linotype", Palatino, "Book Antiqua", Georgia, serif;
    --sans:  ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, Helvetica, Arial, sans-serif;
  }

  /* MARK-ROOT-END */

  @media (prefers-color-scheme: dark) {
    :root {
      --ground: __GROUND_D__;
      --ink:    __INK_D__;
      --pink:   __PINK_D__;
      --pale:   __PALE_D__;
    }
  }

  *, *::before, *::after { box-sizing: border-box; }

  html { -webkit-text-size-adjust: 100%; }

  body {
    margin: 0;
    min-height: 100svh;
    display: flex;
    flex-direction: column;
    background: var(--ground);
    color: var(--ink);
    font-family: var(--serif);
    -webkit-font-smoothing: antialiased;
    text-rendering: optimizeLegibility;
  }

  main {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 3rem 1.5rem 2rem;
    gap: clamp(1.75rem, 5vw, 2.75rem);
  }

  /* ---------- the mark ---------- */

  /* MARK-CSS-START — the preview lifts this block so it cannot drift */

  /*
    Huxley puts the heart at the chest of a 24x24 grid, below the eyes
    and the mouth. The mark is the heart alone -- the face comes off,
    and the grid closes in to the heart's own 5x5 footprint.

    The colourway comes from A to Z of The Designers Republic.
  */

  .mark {
    display: grid;
    grid-template-columns: repeat(5, var(--cell));
    grid-auto-rows: var(--cell);
    gap: var(--gap);
    margin: 0;
    padding: 0;
    list-style: none;
  }

  .mark i {
    display: block;
    background: var(--ink);
    border-radius: 1px;
    opacity: var(--base);
  }

  /*
    The heart is the life signal, and it carries the pink.

    The beat is a ripple, not a blink. Every cell runs the same
    keyframes but starts at its own moment -- the delay is set by the
    cell's distance from the heart's centre -- so the pulse travels
    outward through the shape. The heart reads as alive, breathing
    from the middle out, rather than as a shape switching on and off.
  */
  .mark i.heart {
    background: var(--pink);
    animation: wave __CYCLE__ cubic-bezier(.4, 0, .2, 1) infinite;
    animation-delay: var(--d);
  }

  /*
    A lub-dub, travelling.

    Huxley beats at full strength, drops to half 180ms later, and goes
    dark 360ms after that. Holding each value briefly makes the two
    beats read as two beats rather than one long dimming -- the drop
    between them is the thing your eye catches.

    Huxley's pace is 2200ms, and the crest window closes at 360ms. The
    keyframes below keep that shape: a full crest, a dimmer second
    crest, then rest at the base level.

    The centre cell of the heart stays dimmer throughout, as it does in
    Huxley, so the ripple has a soft core and the shape keeps a focal
    point instead of reading as a solid blob.

    The base level is not zero. The heart never fully vanishes -- it
    rests at a low glow and rises out of it. That is what keeps it
    looking alive between beats.
  */
  @keyframes wave {
    0%        { opacity: var(--peak); }
    4%        { opacity: var(--half); }
    9%, 13%   { opacity: var(--half); }
    17%, 100% { opacity: var(--base); }
  }

  /* MARK-CSS-END */

  /* ---------- the name ---------- */

  h1 {
    margin: 0;
    font-size: clamp(2.1rem, 1rem + 7vw, 4.6rem);
    font-weight: 400;
    line-height: 1;
    letter-spacing: -0.022em;
    text-wrap: balance;
  }
  h1 .tld { color: var(--pink); }

  /* ---------- the standfirst ---------- */

  .standfirst {
    margin: 0;
    max-width: 26rem;
    font-size: clamp(1rem, .95rem + .35vw, 1.125rem);
    line-height: 1.55;
    color: var(--ink);
    text-wrap: balance;
  }

  a:focus-visible {
    outline: 2px solid var(--pink);
    outline-offset: 4px;
  }

  /* ---------- footer ---------- */

  footer {
    display: flex;
    justify-content: center;
    gap: .35rem 1.4rem;
    flex-wrap: wrap;
    padding: 1.5rem 1.5rem 2.25rem;
    font-family: var(--sans);
    font-size: .8125rem;
    color: var(--ink);
  }
  footer a {
    color: inherit;
    text-decoration: none;
    border-bottom: 1px solid transparent;
    transition: color 160ms ease, border-color 160ms ease;
  }
  footer a:hover { color: var(--pink); border-bottom-color: var(--pink); }
  footer .dot { opacity: .45; }

  @media (prefers-reduced-motion: reduce) {
    .mark i.heart { animation: none; opacity: var(--peak); }
    * { transition: none !important; }
  }
</style>
</head>
<body>

<main>

  <div class="mark" role="img" aria-label="A beating heart">
    __CELLS__
  </div>

  <h1>lastknown<span class="tld">.design</span></h1>

  <!--
    No book link here yet. The manuscript is not finished, so the site
    does not advertise it. When the book launches, the door goes back in
    and this comment goes out.
  -->

  <p class="standfirst">
    A practice and a body of work on how AI agents should behave.
  </p>

</main>

<footer>
  <a href="mailto:ian@lastknown.design">ian@lastknown.design</a>
  <span class="dot">&middot;</span>
  <a href="https://github.com/lastknownvoice">@lastknownvoice</a>
</footer>

</body>
</html>
"""


def build():
    # Guard: a unitless animation-delay silently resolves to 0s and
    # collapses the wave back into a single blink. Catch it here rather
    # than discovering it in the browser.
    if "--d:" in mark_cells() and "ms" not in mark_cells():
        raise SystemExit("wave delay is missing its unit -- the wave would collapse")

    html = (
        HTML.replace("__CELLS__", mark_cells())
        .replace("__CYCLE__", CYCLE)
        .replace("__FAVICON__", favicon_uri())
        .replace("__GROUND__", PALETTE["ground"])
        .replace("__INK__", PALETTE["ink"])
        .replace("__PINK__", PALETTE["pink"])
        .replace("__PALE__", PALETTE["pale"])
        .replace("__GROUND_D__", PALETTE_DARK["ground"])
        .replace("__INK_D__", PALETTE_DARK["ink"])
        .replace("__PINK_D__", PALETTE_DARK["pink"])
        .replace("__PALE_D__", PALETTE_DARK["pale"])
    )
    (ROOT / "index.html").write_text(html, encoding="utf-8")
    print(f"wrote {ROOT / 'index.html'}")
    print(f"  character : Huxley — the heart alone")
    print(f"  grid      : {GRID}x{GRID}")
    print(f"  heart     : {len(HEART)} cells, centre ({HEART_CX},{HEART_CY})")
    print(f"  wave      : {len(RINGS)} rings, {WAVE_STEP_MS}ms per ring, {CYCLE} cycle")
    print(f"  base      : {BASE_OPACITY} (heart rests lit, never off)")
    print(f"  palette   : {PALETTE}")


if __name__ == "__main__":
    build()
