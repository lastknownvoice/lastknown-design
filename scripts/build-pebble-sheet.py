#!/usr/bin/env python3
"""Build the Pebbles comparison sheet for lastknown.design.

The site's mark is currently a 7x7 field of squares with a pulse travelling
outward from the centre. We are replacing it with one Pebble character from
Ian's own agent identity system.

This sheet renders all five characters, in two colour treatments, at the
size the mark actually occupies on the page -- so the choice is made against
the real thing rather than a thumbnail.

Geometry and motion are lifted verbatim from the Pebbles library:
  - shapes  -> data.js  (the three parts of each character)
  - motion  -> styles.js (idle drift + shared breath keyframes)

Run:  python3 scripts/build-pebble-sheet.py
Out:  design/pebble-sheet.html
"""

import pathlib

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

# The library's "bold" palette -- the default, and the one the shapes were
# drawn against.
PEBBLES_PALETTE = {
    "Arch": ["#0073F5", "#27D3BC", "#5746B2"],
    "Pip": ["#27D3BC", "#FFC800", "#0073F5"],
    "Block": ["#FFC800", "#FF492C", "#5746B2"],
    "Orbit": ["#FF492C", "#0073F5", "#FFC800"],
    "Offset": ["#5746B2", "#0073F5", "#27D3BC"],
}

# A ramp built from the site's own accent, so the mark stays on-brand.
SITE_PALETTE = {
    "Arch": ["#8a3324", "#b85c43", "#d99a84"],
    "Pip": ["#8a3324", "#c2705a", "#e0ab97"],
    "Block": ["#8a3324", "#a84733", "#cf8570"],
    "Orbit": ["#8a3324", "#c2705a", "#e0ab97"],
    "Offset": ["#8a3324", "#a84733", "#cf8570"],
}

SITE_PALETTE_DARK = {
    name: [cols[2], cols[1], cols[0]] for name, cols in SITE_PALETTE.items()
}

PEBBLES_PALETTE_DARK = {
    "Arch": ["#77B7FF", "#73E1D1", "#B8AAF5"],
    "Pip": ["#73E1D1", "#FFE16A", "#77B7FF"],
    "Block": ["#FFE16A", "#FF806D", "#B8AAF5"],
    "Orbit": ["#FF9B87", "#83BAFF", "#FFE16A"],
    "Offset": ["#B8AAF5", "#77B7FF", "#73E1D1"],
}

ORDER = ["Arch", "Pip", "Block", "Orbit", "Offset"]


def svg_parts(character, colors):
    """Render a character's three parts as inline SVG groups."""
    out = []
    for (tag, attrs), color in zip(SHAPES[character], colors):
        attrs_markup = " ".join(f'{k}="{v}"' for k, v in attrs.items())
        out.append(f'<g class="part p{len(out) + 1}" fill="{color}">'
                   f"<{tag} {attrs_markup} /></g>")
    return "\n          ".join(out)


def pebble_svg(character, colors, size=100, label=None):
    label = label or character
    return f"""<svg viewBox="0 0 100 100" width="{size}" height="{size}" role="img" aria-label="{label}">
          <g class="outer">
          {svg_parts(character, colors)}
          </g>
        </svg>"""


def favicon_markup(character, colors, size=28):
    body = svg_parts(character, colors)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="{size}" height="{size}" role="img" aria-label="{character}">
  <g class="outer">{body}</g>
</svg>"""


def tile(character, colors, palette_name, theme, size=100):
    return f"""      <figure class="tile" data-theme="{theme}">
        <div class="stage">{pebble_svg(character, colors, size)}</div>
        <figcaption><b>{character}</b><span>{palette_name}</span></figcaption>
      </figure>"""


def favicon_tile(character, colors):
    svg = favicon_markup(character, colors)
    uri = (
        "data:image/svg+xml,"
        + svg.replace("<", "%3C").replace(">", "%3E").replace('"', "%22").replace("#", "%23")
    )
    return f"""      <figure class="fav">
        <img src="{uri}" width="28" height="28" alt="" />
        <figcaption>{character}</figcaption>
      </figure>"""


def build():
    pebbles_light = "\n".join(tile(c, PEBBLES_PALETTE[c], "Pebbles bold", "light") for c in ORDER)
    pebbles_dark = "\n".join(tile(c, PEBBLES_PALETTE_DARK[c], "Pebbles bold", "dark") for c in ORDER)
    site_light = "\n".join(tile(c, SITE_PALETTE[c], "Last Known accent", "light") for c in ORDER)
    site_dark = "\n".join(tile(c, SITE_PALETTE_DARK[c], "Last Known accent", "dark") for c in ORDER)
    fav_pebbles = "\n".join(favicon_tile(c, PEBBLES_PALETTE[c]) for c in ORDER)
    fav_site = "\n".join(favicon_tile(c, SITE_PALETTE[c]) for c in ORDER)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Pebbles — mark candidates for lastknown.design</title>
<style>
  :root {{
    --paper: #faf9f6;
    --ink: #171614;
    --ink-soft: #767268;
    --accent: #8a3324;
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
    padding: 3rem 1.5rem 5rem;
  }}

  h1 {{ font-size: 1.6rem; font-weight: 400; margin: 0 0 .35rem; letter-spacing: -.015em; }}
  h2 {{ font-size: .8125rem; font-weight: 500; letter-spacing: .16em; text-transform: uppercase;
        color: var(--ink-soft); margin: 3rem 0 1rem; font-family: var(--sans); }}
  p.lede {{ max-width: 40rem; color: var(--ink-soft); line-height: 1.55; margin: 0 0 1rem; }}
  .row {{
    display: flex; flex-wrap: wrap; gap: 2.5rem 1.75rem;
    padding: 2rem 1.25rem;
    border: 1px solid rgba(23,22,20,.10);
    border-radius: 8px;
  }}
  .row.dark {{ background: #131211; border-color: rgba(236,232,224,.12); }}
  .row.dark .tile figcaption {{ color: #8b867c; }}
  .row.dark .tile figcaption b {{ color: #ece8e0; }}

  .tile {{ margin: 0; text-align: center; width: 140px; }}
  .tile .stage {{
    height: 100px; display: flex; align-items: center; justify-content: center;
    margin-bottom: .7rem;
  }}
  .tile figcaption {{ font-family: var(--sans); font-size: .8125rem; line-height: 1.4; }}
  .tile figcaption b {{ display: block; font-weight: 500; color: var(--ink); }}
  .tile figcaption span {{ color: var(--ink-soft); font-size: .75rem; }}

  .favrow {{ display: flex; flex-wrap: wrap; gap: 1.5rem; padding: 1.25rem; }}
  .fav {{ margin: 0; text-align: center; font-family: var(--sans); font-size: .75rem; color: var(--ink-soft); }}
  .fav figcaption {{ margin-top: .4rem; }}

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
    .part, .outer {{ animation: none !important; }}
  }}
</style>
</head>
<body>

<h1>Which Pebble should be the lastknown.design mark?</h1>
<p class="lede">
  The current mark is a 7&times;7 field of squares with a pulse travelling outward.
  This replaces it with one character from the Pebbles identity system, rendered at
  the size the mark actually occupies on the page. Geometry and motion are the
  library's own &mdash; not a redraw. Pick a character and a colour treatment.
</p>

<h2>Pebbles palette &mdash; light</h2>
<div class="row">
{pebbles_light}
</div>

<h2>Pebbles palette &mdash; dark</h2>
<div class="row dark">
{pebbles_dark}
</div>

<h2>Last Known accent &mdash; light</h2>
<div class="row">
{site_light}
</div>

<h2>Last Known accent &mdash; dark</h2>
<div class="row dark">
{site_dark}
</div>

<h2>Favicon candidates &mdash; Pebbles palette</h2>
<div class="row favrow">
{fav_pebbles}
</div>

<h2>Favicon candidates &mdash; Last Known accent</h2>
<div class="row favrow">
{fav_site}
</div>

</body>
</html>
"""

    out = pathlib.Path(__file__).resolve().parent.parent / "design" / "pebble-sheet.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    build()
