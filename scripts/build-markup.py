#!/usr/bin/env python3
"""Generate the lastknown.design one-pager.

The mark is a 7x7 field of squares with a pulse travelling outward from
the centre -- a voice radiating. Each cell carries four CSS custom
properties so the whole thing stays hand-editable:

    --x --y   position on the grid (0 is centre)
    --d       distance from centre, drives the animation delay
    --o       resting opacity, so the field has a vignette at rest
"""

import math
import pathlib

GRID = 7
HALF = GRID // 2

# The field must read as a solid grid of squares at REST, with a vignette
# that falls off toward the corners. Too low a floor and the mark looks
# broken rather than dim. The pulse is then a highlight travelling over
# a shape that already exists.
FLOOR = 0.22   # corner cells at rest
PEAK = 0.62    # centre cells at rest
FALLOFF = 0.062  # per unit of distance

cells = []
for y in range(-HALF, HALF + 1):
    for x in range(-HALF, HALF + 1):
        d = round(math.hypot(x, y), 2)
        o = round(max(FLOOR, PEAK - d * FALLOFF), 3)
        # Write the final 1-based grid position straight into the markup.
        # `grid-column: calc(var(--x) + 4)` does not work: grid-column-start
        # needs a plain integer, and calc() over a custom property that
        # holds a unitless number is not accepted as one.
        col = x + HALF + 1
        row = y + HALF + 1
        cells.append(
            f'<i style="grid-area:{row}/{col};--d:{d};--o:{o}"></i>'
        )

cells_markup = "\n        ".join(cells)

# Static favicon: the same field, no animation.
icon_cells = "\n".join(
    f'<rect x="{c}" y="{c}" width="4" height="4" fill="#8a3324" opacity="{0.25 + 0.75 * (1 - (abs(x) + abs(y)) / 6):.2f}"/>'
    for y in range(7)
    for x, c in enumerate(range(0, 28, 4))
)
favicon_svg = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 28 28">'
    + icon_cells
    + "</svg>"
)
favicon_uri = (
    "data:image/svg+xml,"
    + favicon_svg.replace("<", "%3C").replace(">", "%3E").replace('"', "%22").replace("#", "%23")
)

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Last Known Voice — how AI agents should behave</title>
<meta name="description" content="Last Known Voice — a free, open field guide to designing AI agents that listen, wait and act. By Ian Roberts.">
<meta property="og:title" content="lastknown.design">
<meta property="og:description" content="A free field guide to designing AI agents that listen, wait and act.">
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

    --cell:       clamp(7px, 2.1vw, 10px);
    --gap:        clamp(3px, 0.85vw, 5px);

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

  .mark {
    display: grid;
    grid-template-columns: repeat(7, var(--cell));
    grid-auto-rows: var(--cell);
    gap: var(--gap);
    margin: 0;
    padding: 0;
    list-style: none;
  }

  .mark i {
    display: block;
    background: var(--accent);
    border-radius: 1px;
    opacity: var(--o);
    transform: scale(1);
    transform-box: fill-box;
    transform-origin: center;
    animation: pulse 2.1s cubic-bezier(.45, 0, .55, 1) infinite;
    animation-delay: calc(var(--d) * 135ms);
  }

  @keyframes pulse {
    0%   { opacity: var(--o);   transform: scale(1); }
    12%  { opacity: 1;          transform: scale(1.22); }
    38%  { opacity: calc(var(--o) * .55); transform: scale(.94); }
    100% { opacity: var(--o);   transform: scale(1); }
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
  h1 .tld { color: var(--accent); }

  /* ---------- the door ---------- */

  .door {
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: .4rem;
    align-items: center;
    max-width: 30rem;
  }

  .door a {
    text-decoration: none;
    display: flex;
    flex-direction: column;
    gap: .45rem;
    align-items: center;
    border-radius: 3px;
  }

  .door .title {
    font-family: var(--sans);
    font-size: 1.0625rem;
    font-weight: 550;
    letter-spacing: -0.005em;
    color: var(--ink);
    text-decoration: underline;
    text-decoration-thickness: 1px;
    text-underline-offset: .22em;
    text-decoration-color: var(--ink-soft);
    transition: text-decoration-color 160ms ease, color 160ms ease;
  }

  .door .note {
    font-size: .9375rem;
    line-height: 1.5;
    color: var(--ink-soft);
  }

  .door a:hover .title { color: var(--accent); text-decoration-color: var(--accent); }
  .door a:hover .note { color: var(--ink); }

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
    .mark i { animation: none; opacity: var(--o); }
    * { transition: none !important; }
  }
</style>
</head>
<body>

<main>

  <ul class="mark" role="img" aria-label="Last Known Voice">
    __CELLS__
  </ul>

  <h1>lastknown<span class="tld">.design</span></h1>

  <p class="door">
    <a href="https://book.lastknown.design/">
      <span class="title">Conversation Is the Control Layer</span>
      <span class="note">A free field guide to designing AI agents that listen, wait and act</span>
    </a>
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

out = pathlib.Path(__file__).resolve().parent.parent / "index.html"
out.write_text(
    HTML.replace("__CELLS__", cells_markup).replace("__FAVICON__", favicon_uri),
    encoding="utf-8",
)
print(f"wrote {out}")
