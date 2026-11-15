#!/usr/bin/env python3
"""Build a side-by-side of the Huxley mark in both colourways.

Both panels are the real page markup, one forced light and one forced
dark, so the comparison is against the thing.

Run:  python3 scripts/build-huxley-preview.py
Out:  design/huxley-preview.html
"""

import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent

# Pull the real cells and CSS out of the generated page so the preview
# cannot drift from what actually ships.
INDEX = (ROOT / "index.html").read_text(encoding="utf-8")

import importlib.util
spec = importlib.util.spec_from_file_location("bm", ROOT / "scripts" / "build-markup.py")
bm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bm)

CELLS = bm.mark_cells()


def panel(theme, ground, ink, pink, pale, label):
    return f"""  <section class="panel {theme}">
    <div class="mark-wrap">
      <div class="mark" role="img" aria-label="Huxley">
        {CELLS}
      </div>
      <h1>lastknown<span class="tld">.design</span></h1>
      <p class="standfirst">A practice and a body of work on how AI agents should behave.</p>
    </div>
    <p class="label">{label}</p>
    <ul class="swatches">
      <li><span style="background:{ground}"></span>ground {ground}</li>
      <li><span style="background:{ink}"></span>ink {ink}</li>
      <li><span style="background:{pink}"></span>pink {pink}</li>
      <li><span style="background:{pale}"></span>pale {pale}</li>
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
    margin: 0; background: #6b6560; color: #171614;
    font-family: ui-sans-serif, -apple-system, sans-serif;
    padding: 2rem; display: flex; gap: 2rem; flex-wrap: wrap;
    align-items: flex-start;
  }}
  .panel {{
    flex: 1 1 340px; padding: 2.5rem 1.5rem 1.5rem;
    border-radius: 10px; position: relative;
    display: flex; flex-direction: column; align-items: center;
  }}
  .panel.light {{ background: {bm.PALETTE['ground']}; color: {bm.PALETTE['ink']}; }}
  .panel.dark  {{ background: {bm.PALETTE_DARK['ground']}; color: {bm.PALETTE_DARK['ink']}; }}

  .mark-wrap {{
    flex: 1; display: flex; flex-direction: column; align-items: center;
    justify-content: center; text-align: center;
    gap: clamp(1.5rem, 4vw, 2.5rem); padding: 1rem 0 2rem;
  }}

  .mark {{
    display: grid; grid-template-columns: repeat(24, 6px);
    grid-auto-rows: 6px; gap: 2px; margin: 0; padding: 0; list-style: none;
  }}
  .mark i {{ display:block; border-radius: 1px; }}
  .panel.light .mark i.eye, .panel.light .mark i.mouth {{ background: {bm.PALETTE['ink']}; }}
  .panel.dark  .mark i.eye, .panel.dark  .mark i.mouth {{ background: {bm.PALETTE_DARK['ink']}; }}
  .panel.light .mark i.heart {{ background: {bm.PALETTE['pink']}; animation: var(--beat, beat) 2.2s cubic-bezier(.4,0,.2,1) infinite; }}
  .panel.dark  .mark i.heart {{ background: {bm.PALETTE_DARK['pink']}; animation: var(--beat, beat) 2.2s cubic-bezier(.4,0,.2,1) infinite; }}

  @keyframes beat {{
    0%, 6% {{opacity:1}} 9% {{opacity:.45}} 13%, 20% {{opacity:.5}} 26%, 100% {{opacity:0}}
  }}
  @keyframes beat-mid {{
    0%, 6% {{opacity:.35}} 9% {{opacity:.16}} 13%, 20% {{opacity:.175}} 26%, 100% {{opacity:0}}
  }}

  h1 {{
    margin: 0; font-size: clamp(1.8rem, 1rem + 5vw, 3.4rem); font-weight: 400;
    line-height: 1; letter-spacing: -.022em;
    font-family: "Iowan Old Style", "Palatino Linotype", Palatino, Georgia, serif;
  }}
  h1 .tld {{ color: {bm.PALETTE['pink']}; }}
  .panel.dark h1 .tld {{ color: {bm.PALETTE_DARK['pink']}; }}

  .standfirst {{
    margin: 0; max-width: 22rem; font-size: 1rem; line-height: 1.55;
    font-family: "Iowan Old Style", "Palatino Linotype", Palatino, Georgia, serif;
  }}

  .label {{
    margin: 0 0 .8rem; font-size: .75rem; letter-spacing: .16em;
    text-transform: uppercase; opacity: .65; font-weight: 500;
  }}
  .swatches {{
    list-style: none; margin: 0; padding: 0; display: flex; flex-wrap: wrap;
    gap: .35rem 1rem; font-size: .75rem; font-family: ui-monospace, monospace;
    opacity: .8;
  }}
  .swatches li {{ display: flex; align-items: center; gap: .4rem; }}
  .swatches span {{ width: .8rem; height: .8rem; border-radius: 2px; border: 1px solid rgba(0,0,0,.2); }}

  @media (prefers-reduced-motion: reduce) {{
    .mark i.heart {{ animation: none !important; opacity: 1; }}
  }}
</style>
</head>
<body>

{panel("light", bm.PALETTE["ground"], bm.PALETTE["ink"], bm.PALETTE["pink"], bm.PALETTE["pale"], "Light — Designers Republic orange")}

{panel("dark", bm.PALETTE_DARK["ground"], bm.PALETTE_DARK["ink"], bm.PALETTE_DARK["pink"], bm.PALETTE_DARK["pale"], "Dark — re-grounded on ink")}

</body>
</html>
"""

out = ROOT / "design" / "huxley-preview.html"
out.parent.mkdir(exist_ok=True)
out.write_text(HTML, encoding="utf-8")
print(f"wrote {out}")
