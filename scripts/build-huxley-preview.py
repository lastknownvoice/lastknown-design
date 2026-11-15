#!/usr/bin/env python3
"""Build a side-by-side of the mark in both colourways.

Both panels are the real page markup, and the CSS is lifted straight out
of the generated `index.html`, so the preview cannot drift from what
actually ships. Only the palette custom properties are overridden per
panel -- everything else is the real thing.

Run:  python3 scripts/build-huxley-preview.py
Out:  design/huxley-preview.html
"""

import importlib.util
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent

spec = importlib.util.spec_from_file_location("bm", ROOT / "scripts" / "build-markup.py")
bm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bm)

CELLS = bm.mark_cells()

# Pull the real mark stylesheet out of the shipped page. The markers
# bracket just the mark's rules, so the preview gets the real animation
# without inheriting the page's body/main layout. The root block comes
# too, because it holds --cell and --gap.
INDEX = (ROOT / "index.html").read_text(encoding="utf-8")

style_match = re.search(
    r"MARK-CSS-START.*?\*/(.*?)/\* MARK-CSS-END", INDEX, re.S
)
if not style_match:
    raise SystemExit("could not find the mark CSS markers in index.html")

root_match = re.search(r":root\s*\{(.*?)\}", INDEX, re.S)
if not root_match:
    raise SystemExit("could not find the :root block in index.html")

# Interpolated values are inserted verbatim -- their braces are not
# re-processed by the f-string, so they must NOT be doubled. Doubling
# here emits literal `{{` into the CSS, which silently kills the rules.
REAL_CSS = style_match.group(1)
ROOT_CSS = root_match.group(1)


def panel_vars(theme, palette):
    """One panel's colourway, as CSS custom property overrides."""
    return (
        f"  .panel.{theme} {{\n"
        f"    --ground: {palette['ground']};\n"
        f"    --ink: {palette['ink']};\n"
        f"    --pink: {palette['pink']};\n"
        f"    --pale: {palette['pale']};\n"
        f"    background: var(--ground);\n"
        f"    color: var(--ink);\n"
        f"  }}\n"
    )


PANEL_CSS = panel_vars("light", bm.PALETTE) + panel_vars("dark", bm.PALETTE_DARK)


def panel(theme, palette, label):
    return f"""  <section class="panel {theme}">
    <div class="mark-wrap">
      <div class="mark" role="img" aria-label="A beating heart">
        {CELLS}
      </div>
      <h1>lastknown<span class="tld">.design</span></h1>
      <p class="standfirst">A practice and a body of work on how AI agents should behave.</p>
    </div>
    <p class="label">{label}</p>
    <ul class="swatches">
      <li><span style="background:{palette['ground']}"></span>ground {palette['ground']}</li>
      <li><span style="background:{palette['ink']}"></span>ink {palette['ink']}</li>
      <li><span style="background:{palette['pink']}"></span>pink {palette['pink']}</li>
      <li><span style="background:{palette['pale']}"></span>pale {palette['pale']}</li>
    </ul>
  </section>"""


HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Huxley mark — light and dark</title>
<style>
  * {{ box-sizing: border-box; }}

  body {{
    margin: 0;
    background: #6b6560;
    color: #171614;
    font-family: ui-sans-serif, -apple-system, sans-serif;
    padding: 2rem;
    display: flex;
    gap: 2rem;
    flex-wrap: wrap;
    align-items: flex-start;
  }}

  /* ---- the real stylesheet from index.html ---- */
  :root {{ {ROOT_CSS} }}
{REAL_CSS}

  /* ---- the preview's own chrome ---- */
{PANEL_CSS}
  .panel {{
    flex: 1 1 340px;
    padding: 2.5rem 1.5rem 1.5rem;
    border-radius: 10px;
    display: flex;
    flex-direction: column;
    align-items: center;
  }}

  .mark-wrap {{
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    gap: clamp(1.5rem, 4vw, 2.5rem);
    padding: 1rem 0 2rem;
  }}

  .mark {{
    grid-template-columns: repeat(5, 14px);
    grid-auto-rows: 14px;
    gap: 4px;
  }}

  .label {{
    margin: 0 0 .8rem;
    font-size: .75rem;
    letter-spacing: .16em;
    text-transform: uppercase;
    opacity: .65;
    font-weight: 500;
  }}

  .swatches {{
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-wrap: wrap;
    gap: .35rem 1rem;
    font-size: .75rem;
    font-family: ui-monospace, monospace;
    opacity: .8;
  }}
  .swatches li {{ display: flex; align-items: center; gap: .4rem; }}
  .swatches span {{
    width: .8rem; height: .8rem; border-radius: 2px;
    border: 1px solid rgba(0,0,0,.2);
  }}
</style>
</head>
<body>

{panel("light", bm.PALETTE, "Light — Designers Republic orange")}

{panel("dark", bm.PALETTE_DARK, "Dark — re-grounded on ink")}

</body>
</html>
"""

out = ROOT / "design" / "huxley-preview.html"
out.parent.mkdir(exist_ok=True)
out.write_text(HTML, encoding="utf-8")
print(f"wrote {out}")
print("  css      : lifted from index.html")
print(f"  wave     : {len(bm.RINGS)} rings, {bm.WAVE_STEP_MS}ms per ring")
