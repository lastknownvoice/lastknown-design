#!/usr/bin/env python3
"""Generate the lastknown.design one-pager.

The mark is **Arch** — a character from Ian's Pebbles agent identity
system: a rounded arch body, a tall rounded rect, and a circle, each in
its own colour, overlapping.

Geometry and motion are read from the vendored Pebbles library in
`pebbles/` (data.js and styles.js) rather than transcribed, so the mark
stays in step with the source of truth. If the library changes, this
picks the change up.

The character is drawn at the size the mark occupies on the page, on the
site's own background, in the site's own accent.

Run:  python3 scripts/build-markup.py
Out:  index.html
"""

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent

# --------------------------------------------------------------------------
# Read the geometry out of the vendored library
# --------------------------------------------------------------------------

CHARACTER = "Arch"
PALETTE = "accent"        # the library's own palette names
THEME = "auto"            # light or dark follows the OS


def load_shapes():
    """Parse the `shapes` array out of data.js.

    The file is one long line of JS. Rather than pull in a JS runtime,
    we read the array literal and pull out the parts we need with a
    small regex. The shape we use is a path, a rect and a circle, so
    the attribute values are simple enough to parse directly.
    """
    source = (ROOT / "pebbles" / "data.js").read_text(encoding="utf-8")

    # Each shape is: {name:'Arch',family:'...',parts:[[tag,{attrs}],[...]]}
    pattern = re.compile(
        r"\{name:'(?P<name>[^']+)'"
        r"(?:,family:'[^']*')?"
        r",parts:\[(?P<parts>.*?)\]\}"
    )
    for match in pattern.finditer(source):
        if match.group("name") != CHARACTER:
            continue
        return parse_parts(match.group("parts"))
    raise SystemExit(f"could not find character {CHARACTER!r} in pebbles/data.js")


def parse_parts(raw):
    """Turn `['path',{d:'M12...'}],['rect',{x:46,...}]` into a list."""
    parts = []
    for tag, attrs in re.findall(
        r"\['(?P<tag>[a-z]+)',\{(?P<attrs>[^}]*)\}\]", raw
    ):
        attributes = {}
        for key, value in re.findall(r"(\w+):('[^']*'|[-\d.]+)", attrs):
            attributes[key] = value.strip("'")
        parts.append((tag, attributes))
    return parts


def load_colors():
    """Pull the palette colours for our character out of data.js.

    Both `palettes` and `paletteDarkVariants` are objects of objects, so
    we walk them with a brace matcher rather than a regex -- nested
    braces defeat the obvious pattern.

    Returns (light_colours, dark_colours). Dark comes from the library's
    own `paletteDarkVariants`, which is what the component uses when the
    OS is in dark mode.
    """
    source = (ROOT / "pebbles" / "data.js").read_text(encoding="utf-8")

    def read(block):
        # Match the declaration exactly -- `palettes` is a substring of
        # `paletteDarkVariants`, so a plain find() would match the wrong
        # one.
        match = re.search(rf"export const {block}\s*=\s*\{{", source)
        if not match:
            return None
        body, _ = _balanced_object(source, match.end() - 1)
        palette_body = _member(body, PALETTE)
        if palette_body is None:
            return None
        colors = _member(palette_body, CHARACTER)
        if not colors:
            return None
        return re.findall(r"#[0-9A-Fa-f]{6}", colors)

    light = read("palettes")
    dark = read("paletteDarkVariants")
    if not light:
        raise SystemExit(f"could not find palette {PALETTE!r} in pebbles/data.js")
    return light, dark or light


def _balanced_object(source, start):
    """Return (inner_text, end_index) for a brace-delimited object."""
    depth = 0
    for index in range(start, len(source)):
        if source[index] == "{":
            depth += 1
        elif source[index] == "}":
            depth -= 1
            if depth == 0:
                return source[start + 1:index], index
    raise SystemExit("unbalanced braces in data.js")


def _member(body, key):
    """Find `key:[...]` or `key:{...}` inside an object body.

    The body may start with whitespace or a newline before its first
    member, so the boundary check allows any non-identifier character
    before the key rather than only `,` or `{`.
    """
    match = re.search(rf"(?:^|[^A-Za-z0-9_$]){re.escape(key)}\s*:", body)
    if not match:
        return None
    rest = body[match.end():]
    if rest.lstrip().startswith("["):
        open_at = body.index("[", match.end())
        close = body.index("]", open_at)
        return body[open_at:close + 1]
    open_at = body.index("{", match.end())
    inner, _ = _balanced_object(body, open_at)
    return inner


def load_idle_motion():
    """Pull the idle drift + breath keyframes out of styles.js.

    The library keeps all motion in one stylesheet string. We take the
    idle rules and the four keyframes they reference.
    """
    source = (ROOT / "pebbles" / "styles.js").read_text(encoding="utf-8")
    # The stylesheet is a JS string literal; unescape the few things we need.
    source = source.replace("\\n", "\n")

    wanted = ["drift", "drift2", "drift3", "breath"]
    out = {}
    for name in wanted:
        match = re.search(
            rf"@keyframes {name}\s*\{{(.*?)\}}\s*(?=@keyframes|\.agent|$)", source, re.S
        )
        if match:
            out[name] = match.group(1).strip()
    if len(out) != len(wanted):
        raise SystemExit(f"missing keyframes: {set(wanted) - set(out)}")
    return out


SHAPES = load_shapes()
COLORS, COLORS_DARK = load_colors()
MOTION = load_idle_motion()


# --------------------------------------------------------------------------
# Markup
# --------------------------------------------------------------------------

def pebble_markup():
    """The three parts as SVG groups, ready to drop into the page.

    Each part carries both colour sets. Light is the default; the dark
    media query swaps to the library's dark palette variants, which is
    how the component itself handles the OS theme.
    """
    out = []
    for index, (tag, attributes) in enumerate(SHAPES):
        attrs = " ".join(f'{k}="{v}"' for k, v in attributes.items())
        light = COLORS[index]
        dark = COLORS_DARK[index]
        fill = light if light == dark else f"{light}; --dark-fill: {dark}"
        out.append(
            f'<g class="part p{index + 1}" style="fill: {fill}">'
            f"<{tag} {attrs} /></g>"
        )
    return "\n          ".join(out)


def favicon_markup():
    """A still Arch for the favicon -- same geometry, no motion."""
    body = "\n  ".join(
        f'<g fill="{COLORS[index]}"><{tag} '
        + " ".join(f'{k}="{v}"' for k, v in attributes.items())
        + " /></g>"
        for index, (tag, attributes) in enumerate(SHAPES)
    )
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
        + body
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
<meta name="theme-color" content="#faf9f6" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#131211" media="(prefers-color-scheme: dark)">
<link rel="canonical" href="https://lastknown.design/">
<link rel="icon" href="__FAVICON__">

<style>
  :root {
    --paper:      #faf9f6;
    --ink:        #171614;
    --ink-soft:   #767268;
    --accent:     #8a3324;

    --mark-size:  clamp(84px, 20vw, 128px);

    --serif: "Iowan Old Style", "Palatino Linotype", Palatino, "Book Antiqua", Georgia, serif;
    --sans:  ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, Helvetica, Arial, sans-serif;
  }

  @media (prefers-color-scheme: dark) {
    :root {
      --paper:    #131211;
      --ink:      #ece8e0;
      --ink-soft: #8b867c;
      --accent:   #e08b74;
    }
  }

  *, *::before, *::after { box-sizing: border-box; }

  html { -webkit-text-size-adjust: 100%; }

  body {
    margin: 0;
    min-height: 100svh;
    display: flex;
    flex-direction: column;
    background: var(--paper);
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
    Arch, from the Pebbles agent identity system.

    The three parts drift independently on a slow loop while the whole
    form breathes. Motion, colours and geometry come from the library --
    see pebbles/data.js and pebbles/styles.js.
  */

  .mark {
    width: var(--mark-size);
    height: var(--mark-size);
    margin: 0;
    padding: 0;
    list-style: none;
    display: block;
  }

  .mark svg {
    display: block;
    width: 100%;
    height: 100%;
    overflow: visible;
  }

  .mark .part,
  .mark .outer {
    transform-box: view-box;
    transform-origin: center;
  }

  .mark .part.p1 { animation: drift  calc(3.8s / var(--speed, 1)) ease-in-out infinite; }
  .mark .part.p2 { animation: drift2 calc(4.2s / var(--speed, 1)) ease-in-out infinite; }
  .mark .part.p3 { animation: drift3 calc(3.3s / var(--speed, 1)) ease-in-out infinite; }
  .mark .outer   { animation: breath calc(5s   / var(--speed, 1)) ease-in-out infinite; }

  /* The library keeps a dark palette for every colourway. Swap to it
     when the OS is dark, the same way the component does. */
  @media (prefers-color-scheme: dark) {
    .mark .part { fill: var(--dark-fill); }
  }

__MOTION__

  /* ---------- the name ---------- */

  h1 {
    margin: 0;
    font-size: clamp(2.1rem, 1rem + 7vw, 4.6rem);
    font-weight: 400;
    line-height: 1;
    letter-spacing: -0.022em;
    text-wrap: balance;
  }
  h1 .tld { color: var(--accent); }

  /* ---------- the standfirst ---------- */

  .standfirst {
    margin: 0;
    max-width: 26rem;
    font-size: clamp(1rem, .95rem + .35vw, 1.125rem);
    line-height: 1.55;
    color: var(--ink-soft);
    text-wrap: balance;
  }

  a:focus-visible {
    outline: 2px solid var(--accent);
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
    color: var(--ink-soft);
  }
  footer a {
    color: inherit;
    text-decoration: none;
    border-bottom: 1px solid transparent;
    transition: color 160ms ease, border-color 160ms ease;
  }
  footer a:hover { color: var(--accent); border-bottom-color: var(--accent); }
  footer .dot { color: var(--ink-soft); opacity: .5; }

  @media (prefers-reduced-motion: reduce) {
    .mark .part, .mark .outer { animation: none; }
    * { transition: none !important; }
  }
</style>
</head>
<body>

<main>

  <div class="mark" role="img" aria-label="Last Known Design">
    <svg viewBox="0 0 100 100" aria-hidden="true">
      <g class="outer">
          __PEBBLE__
      </g>
    </svg>
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
    motion_css = "\n\n".join(
        f"  @keyframes {name} {{ {body} }}" for name, body in MOTION.items()
    )
    html = (
        HTML.replace("__PEBBLE__", pebble_markup())
        .replace("__MOTION__", motion_css)
        .replace("__FAVICON__", favicon_uri())
    )
    (ROOT / "index.html").write_text(html, encoding="utf-8")
    print(f"wrote {ROOT / 'index.html'}")
    print(f"  character : {CHARACTER}")
    print(f"  palette   : {PALETTE} -> {COLORS}")
    print(f"  parts     : {[tag for tag, _ in SHAPES]}")


if __name__ == "__main__":
    build()
