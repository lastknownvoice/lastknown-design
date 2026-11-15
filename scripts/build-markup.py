#!/usr/bin/env python3
"""Generate the lastknown.design one-pager.

The mark is **Huxley** — the 24x24 cellular canvas: X-shaped eyes, a
neutral mouth, and a heart at the chest that beats.

The colourway is taken from *A to Z of The Designers Republic* (Thames &
Hudson): an orange ground, a near-black graphic, a hot pink accent and
a pale peach for text.

Geometry and motion are lifted from the Huxley source so the mark is the
same character, not a redraw:

  - shape     -> dev/huxley/huxley-24.js (eyes, mouth, heart)
  - timing    -> dev/huxley/huxley-24.js (the lub-dub heartbeat)
  - palette   -> sampled from the Designers Republic cover

The character is drawn in SVG, so the page stays a single static file
with no canvas and no runtime. The heartbeat is CSS keyframes matching
the lub-dub shape: a hard full-strength beat, a half-strength beat 180ms
later, then dark.

Run:  python3 scripts/build-markup.py
Out:  index.html
"""

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

# The heart sits at the chest on a 24x24 grid.
GRID = 24
HEART_CX = 12
HEART_CY = 19

# Eyes: 5x5 X shapes, centred at (7, 8) and (16, 8).
EYE_SIZE = 5
EYE_L = (7, 8)
EYE_R = (16, 8)

# Mouth: a 2-row neutral line, cols 7..16, rows 14..15.
MOUTH_COLS = range(7, 17)
MOUTH_ROWS = (14, 15)


def heart_cells():
    """The heart as (col, row) pairs on the 24x24 grid."""
    return [(HEART_CX + lx, HEART_CY + ly) for lx, ly in HEART]


def eye_cells(cx, cy):
    """A 5x5 X: the two diagonals, with the centre dimmed."""
    half = EYE_SIZE // 2
    cells = []
    for dy in range(-half, half + 1):
        for dx in range(-half, half + 1):
            if abs(dx) == abs(dy):
                cells.append((cx + dx, cy + dy, 0.22 if (dx == 0 and dy == 0) else 1.0))
    return cells


def mouth_cells():
    """A 2-row flat mouth, cols 7..16."""
    return [(x, y, 1.0) for y in MOUTH_ROWS for x in MOUTH_COLS]


# --------------------------------------------------------------------------
# Markup
# --------------------------------------------------------------------------

def cell(col, row, cls, opacity=1.0, extra=""):
    """One grid cell as a div, positioned with the CSS grid."""
    # `extra` is appended as further declarations, so it needs its own
    # leading semicolon.
    suffix = f";{extra}" if extra else ""
    return (
        f'<i class="c {cls}" style="grid-area:{row + 1}/{col + 1};'
        f'--o:{opacity}{suffix}"></i>'
    )


def mark_cells():
    """Every lit cell of the character, with its class."""
    out = []
    for col, row, opacity in eye_cells(*EYE_L) + eye_cells(*EYE_R):
        out.append(cell(col, row, "eye", opacity))
    for col, row, opacity in mouth_cells():
        out.append(cell(col, row, "mouth", opacity))
    for col, row in heart_cells():
        # The centre cell of the heart is the focal point and stays
        # dimmer, as it does in Huxley.
        is_center = (col == HEART_CX and row == HEART_CY)
        out.append(
            cell(col, row, "heart", extra="--beat: beat-mid" if is_center else "")
        )
    return "\n        ".join(out)


def favicon_markup():
    """A still heart for the favicon — the mark's focal point.

    At 16px the whole 24x24 character is mush, so the favicon carries
    the heart alone: it is the part that reads at small sizes and the
    part that carries the beat.
    """
    cells = []
    for col, row in heart_cells():
        x = (col - HEART_CX) * 4 + 32
        y = (row - HEART_CY) * 4 + 32
        cells.append(f'<rect x="{x}" y="{y}" width="4" height="4" fill="{PALETTE["pink"]}"/>')
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

    --cell:    clamp(4px, 1.1vw, 6px);
    --gap:     clamp(1.5px, .42vw, 2.5px);

    --serif: "Iowan Old Style", "Palatino Linotype", Palatino, "Book Antiqua", Georgia, serif;
    --sans:  ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, Helvetica, Arial, sans-serif;
  }

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

  /*
    Huxley, the 24x24 cellular canvas: X-shaped eyes, a neutral mouth,
    and a heart at the chest that beats.

    The shape and the lub-dub timing come from the Huxley source. The
    colourway comes from A to Z of The Designers Republic.
  */

  .mark {
    display: grid;
    grid-template-columns: repeat(24, var(--cell));
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
    opacity: var(--o);
  }

  .mark i.eye   { background: var(--ink); }
  .mark i.mouth { background: var(--ink); }

  /* The heart is the life signal, and it carries the pink. */
  .mark i.heart {
    background: var(--pink);
    animation: var(--beat, beat) 2.2s cubic-bezier(.4, 0, .2, 1) infinite;
  }

  /*
    A lub-dub, not a fade.

    Huxley beats at full strength, drops to half 180ms later, and goes
    dark 360ms after that. Holding each value briefly makes the two
    beats read as two beats rather than one long dimming -- the drop
    between them is the thing your eye catches.

    The centre cell of the heart stays dimmer throughout, as it does in
    Huxley, so the shape has a focal point instead of reading as a
    solid blob.
  */
  @keyframes beat {
    0%, 6%   { opacity: 1; }
    9%       { opacity: .45; }
    13%, 20% { opacity: .5; }
    26%, 100% { opacity: 0; }
  }

  @keyframes beat-mid {
    0%, 6%   { opacity: .35; }
    9%       { opacity: .16; }
    13%, 20% { opacity: .175; }
    26%, 100% { opacity: 0; }
  }

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
    .mark i.heart { animation: none; opacity: 1; }
    * { transition: none !important; }
  }
</style>
</head>
<body>

<main>

  <div class="mark" role="img" aria-label="Huxley, a cellular canvas character with a beating heart">
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
    html = (
        HTML.replace("__CELLS__", mark_cells())
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
    print(f"  character : Huxley (24x24 cellular canvas)")
    print(f"  heart     : {len(HEART)} cells, centre ({HEART_CX},{HEART_CY})")
    print(f"  palette   : {PALETTE}")


if __name__ == "__main__":
    build()
