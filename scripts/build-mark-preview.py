#!/usr/bin/env python3
"""Build the mark-preview sheet for lastknown.design.

Two panels:

  1. NOW   -- the current 7x7 square grid, rendered exactly as the live
              site renders it (same clamp() sizing, same vignette, same
              pulse), at both ends of its responsive range.
  2. NEXT  -- one Pebble per candidate character, at the same two sizes.

Both panels sit on the site's real background and use the site's real
type, so the comparison is against the thing, not a thumbnail.

The current mark and its vignette maths are lifted verbatim from
scripts/build-markup.py. The Pebble geometry and idle motion are lifted
verbatim from the Pebbles library (data.js / styles.js).

Run:  python3 scripts/build-mark-preview.py
Out:  design/mark-preview.html
"""

import math
import pathlib

# --------------------------------------------------------------------------
# The current mark, verbatim from build-markup.py
# --------------------------------------------------------------------------

GRID = 7
HALF = GRID // 2
FLOOR = 0.22
PEAK = 0.62
FALLOFF = 0.062


def current_mark_cells():
    cells = []
    for y in range(-HALF, HALF + 1):
        for x in range(-HALF, HALF + 1):
            d = round(math.hypot(x, y), 2)
            o = round(max(FLOOR, PEAK - d * FALLOFF), 3)
            col = x + HALF + 1
            row = y + HALF + 1
            cells.append(
                f'<i style="grid-area:{row}/{col};--d:{d};--o:{o}"></i>'
            )
    return "\n        ".join(cells)


# --------------------------------------------------------------------------
# Pebbles geometry, verbatim from the library's data.js
# --------------------------------------------------------------------------

SHAPES = {
    "Arch": [
        ("path", {"d": "M12 83V45a26 26 0 0 1 52 0v38Z"}),
        ("rect", {"x": 46, "y": 16, "width": 40, "height": 49, "rx": 19}),
        ("circle", {"cx": 73, "cy": 73, "r": 17}),
    ],
    "Pip": [
        ("rect", {"x": 17, "y": 14, "width": 49, "height": 69, "rx": 24}),
        ("circle", {"cx": 66, "cy": 42, "r": 20}),
        ("circle", {"cx": 66, "cy": 65, "r": 16}),
    ],
    "Block": [
        ("rect", {"x": 13, "y": 17, "width": 60, "height": 60, "rx": 13}),
        ("circle", {"cx": 69, "cy": 43, "r": 21}),
        ("rect", {"x": 39, "y": 55, "width": 55, "height": 29, "rx": 14.5}),
    ],
    "Orbit": [
        ("circle", {"cx": 44, "cy": 52, "r": 32}),
        ("rect", {"x": 47, "y": 17.5, "width": 38, "height": 44, "rx": 19}),
        ("circle", {"cx": 65, "cy": 64, "r": 18}),
    ],
    "Offset": [
        ("rect", {"x": 19, "y": 14, "width": 43, "height": 73, "rx": 21}),
        ("rect", {"x": 40, "y": 43, "width": 49, "height": 29, "rx": 14.5}),
        ("circle", {"cx": 71, "cy": 41, "r": 17}),
    ],
}

PEBBLES_PALETTE = {
    "Arch": ["#0073F5", "#27D3BC", "#5746B2"],
    "Pip": ["#27D3BC", "#FFC800", "#0073F5"],
    "Block": ["#FFC800", "#FF492C", "#5746B2"],
    "Orbit": ["#FF492C", "#0073F5", "#FFC800"],
    "Offset": ["#5746B2", "#0073F5", "#27D3BC"],
}

PEBBLES_PALETTE_DARK = {
    "Arch": ["#77B7FF", "#73E1D1", "#B8AAF5"],
    "Pip": ["#73E1D1", "#FFE16A", "#77B7FF"],
    "Block": ["#FFE16A", "#FF806D", "#B8AAF5"],
    "Orbit": ["#FF9B87", "#83BAFF", "#FFE16A"],
    "Offset": ["#B8AAF5", "#77B7FF", "#73E1D1"],
}

# The site's accent, warmed into a three-step ramp so the overlapping
# parts still read as separate -- the same job the Pebbles palette does.
ACCENT = "#8a3324"
ACCENT_LIGHT = ["#8a3324", "#c2705a", "#e0ab97"]
ACCENT_DARK = ["#e08b74", "#c2705a", "#8a3324"]

ORDER = ["Arch", "Pip", "Block", "Orbit", "Offset"]


def pebble_parts(character, colors):
    out = []
    for i, ((tag, attrs), color) in enumerate(zip(SHAPES[character], colors)):
        attrs_markup = " ".join(f'{k}="{v}"' for k, v in attrs.items())
        out.append(
            f'<g class="part p{i + 1}" fill="{color}"><{tag} {attrs_markup} /></g>'
        )
    return "\n            ".join(out)


def pebble_svg(character, colors, size):
    return f"""<svg viewBox="0 0 100 100" width="{size}" height="{size}" role="img" aria-label="{character}">
            <g class="outer">
            {pebble_parts(character, colors)}
            </g>
          </svg>"""


def build():
    now_small = current_mark_cells()
    now_large = current_mark_cells()

    rows_pebbles = []
    rows_accent = []
    for character in ORDER:
        rows_pebbles.append(f"""      <figure class="cand">
        <div class="pair">
          <div class="frame"><ul class="mark small">{pebble_svg(character, PEBBLES_PALETTE[character], 67)}</ul></div>
          <div class="frame"><ul class="mark small">{pebble_svg(character, PEBBLES_PALETTE[character], 100)}</ul></div>
        </div>
        <figcaption>{character}</figcaption>
      </figure>""")
        rows_accent.append(f"""      <figure class="cand">
        <div class="pair">
          <div class="frame"><ul class="mark small">{pebble_svg(character, ACCENT_LIGHT, 67)}</ul></div>
          <div class="frame"><ul class="mark small">{pebble_svg(character, ACCENT_LIGHT, 100)}</ul></div>
        </div>
        <figcaption>{character}</figcaption>
      </figure>""")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>lastknown.design — mark, now and next</title>
<style>
  :root {{
    --paper: #faf9f6;
    --ink: #171614;
    --ink-soft: #767268;
    --accent: #8a3324;
    --cell: 10px;
    --gap: 5px;
    --serif: "Iowan Old Style", "Palatino Linotype", Palatino, "Book Antiqua", Georgia, serif;
    --sans: ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, Helvetica, Arial, sans-serif;
  }}

  *, *::before, *::after {{ box-sizing: border-box; }}

  body {{
    margin: 0;
    background: var(--paper);
    color: var(--ink);
    font-family: var(--serif);
    -webkit-font-smoothing: antialiased;
    padding: 2.5rem 1.5rem 4rem;
  }}

  h1 {{ font-size: 1.5rem; font-weight: 400; margin: 0 0 .3rem; letter-spacing: -.015em; }}
  h1 .tld {{ color: var(--accent); }}
  p.lede {{ max-width: 38rem; color: var(--ink-soft); line-height: 1.55; margin: 0 0 2rem; }}

  h2 {{
    font-family: var(--sans); font-size: .75rem; font-weight: 500;
    letter-spacing: .16em; text-transform: uppercase; color: var(--ink-soft);
    margin: 2.5rem 0 1rem; padding-bottom: .5rem;
    border-bottom: 1px solid rgba(23,22,20,.10);
  }}

  .cands {{
    display: flex; flex-wrap: wrap; gap: 2.25rem 1.5rem;
  }}
  .cand {{ margin: 0; text-align: center; }}
  .pair {{ display: flex; align-items: flex-end; gap: 1rem; }}
  .frame {{
    width: 112px; height: 112px; display: flex;
    align-items: center; justify-content: center;
    background: var(--paper); border: 1px solid rgba(23,22,20,.10);
    border-radius: 6px;
  }}
  .cand figcaption {{
    font-family: var(--sans); font-size: .8125rem; margin-top: .6rem; color: var(--ink);
  }}

  /* ---- current mark, exactly as the site renders it ---- */
  .mark {{
    display: grid;
    grid-template-columns: repeat(7, var(--cell));
    grid-auto-rows: var(--cell);
    gap: var(--gap);
    margin: 0; padding: 0; list-style: none;
  }}
  .mark i {{
    display: block; background: var(--accent); border-radius: 1px;
    opacity: var(--o); transform: scale(1);
    transform-box: fill-box; transform-origin: center;
    animation: pulse 2.1s cubic-bezier(.45, 0, .55, 1) infinite;
    animation-delay: calc(var(--d) * 135ms);
  }}
  .mark.small {{ --cell: 7px; --gap: 3px; }}
  .mark svg {{ display: block; }}

  @keyframes pulse {{
    0%   {{ opacity: var(--o);   transform: scale(1); }}
    12%  {{ opacity: 1;          transform: scale(1.22); }}
    38%  {{ opacity: calc(var(--o) * .55); transform: scale(.94); }}
    100% {{ opacity: var(--o);   transform: scale(1); }}
  }}

  /* ---- Pebbles idle motion, verbatim from the library's styles.js ---- */
  .part, .outer {{ transform-box: view-box; transform-origin: center; }}
  .part.p1 {{ animation: drift calc(3.8s / var(--speed,1)) ease-in-out infinite; }}
  .part.p2 {{ animation: drift2 calc(4.2s / var(--speed,1)) ease-in-out infinite; }}
  .part.p3 {{ animation: drift3 calc(3.3s / var(--speed,1)) ease-in-out infinite; }}
  .outer  {{ animation: breath calc(5s / var(--speed,1)) ease-in-out infinite; }}

  @keyframes drift  {{ 0%,100% {{ transform: translate(0,0); }} 50% {{ transform: translate(calc(1.5px * var(--motion-amp,1)), calc(2px * var(--motion-amp,1))); }} }}
  @keyframes drift2 {{ 0%,100% {{ transform: translate(0,0); }} 50% {{ transform: translate(calc(3px * var(--motion-amp,1)), calc(-2px * var(--motion-amp,1))); }} }}
  @keyframes drift3 {{ 0%,100% {{ transform: translate(0,0); }} 50% {{ transform: translate(calc(-2px * var(--motion-amp,1)), calc(2px * var(--motion-amp,1))); }} }}
  @keyframes breath {{ 0%,100% {{ transform: scale(1); }} 50% {{ transform: scale(calc(1 + .035 * var(--motion-amp,1))); }} }}

  @media (prefers-reduced-motion: reduce) {{
    .part, .outer, .mark i {{ animation: none !important; }}
  }}
</style>
</head>
<body>

<h1>lastknown<span class="tld">.design</span> &mdash; the mark, now and next</h1>
<p class="lede">
  Top row: the mark as it stands today, at both ends of its responsive range.
  Below: each Pebble character at the same two sizes, in the Pebbles palette
  and in a Last Known accent ramp. Geometry and motion are the library's own.
</p>

<h2>Now &mdash; the 7&times;7 square field</h2>
<div class="cands">
  <figure class="cand">
    <div class="pair">
      <div class="frame"><ul class="mark small">
        {now_small}
      </ul></div>
      <div class="frame"><ul class="mark">
        {now_large}
      </ul></div>
    </div>
    <figcaption>current</figcaption>
  </figure>
</div>

<h2>Next &mdash; Pebbles palette</h2>
<div class="cands">
{"".join(rows_pebbles)}
</div>

<h2>Next &mdash; Last Known accent</h2>
<div class="cands">
{"".join(rows_accent)}
</div>

</body>
</html>
"""

    out = pathlib.Path(__file__).resolve().parent.parent / "design" / "mark-preview.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    build()
