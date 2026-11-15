# lastknown.design

The one-pager for [Last Known Voice](https://lastknown.design) — a brand
splash: the mark, the name, one door to the book, and a way to get in touch.

## Structure

| Path | What it is |
|---|---|
| `index.html` | The whole site — markup, CSS and copy in one file |
| `scripts/build-markup.py` | Generates `index.html` from the Huxley source |
| `scripts/build-huxley-preview.py` | Builds the light/dark comparison sheet |
| `design/` | Comparison sheets used to choose the mark |
| `CNAME` | The custom domain (`lastknown.design`) |
| `.github/workflows/deploy-site.yml` | Copies `index.html` to `_site/` and deploys via the official Pages actions |

## The mark

**A beating heart** — Huxley's heart, and only Huxley's heart.

Huxley puts the heart at the chest of a 24×24 cellular canvas, below the
eyes and the mouth. The mark is the heart alone: the face comes off, and
the grid closes in to the heart's own 5×5 footprint. The cells get
proportionally bigger to hold the mark's presence on the page.

Shape and timing come from the Huxley source at `~/dev/huxley/huxley-24.js`.
`scripts/build-markup.py` reads the heart's cell offsets out of it, so the
mark is the same character rather than a redraw.

```bash
python3 scripts/build-markup.py
```

The character is drawn in CSS grid, so the page stays one static file —
no canvas, no runtime, no JavaScript.

**The beat** is a lub-dub, not a fade: full strength, a drop to half, a
held plateau, then dark. The centre cell of the heart stays dimmer
throughout (0.35 against 1.0), as it does in Huxley, so the shape keeps a
focal point. The animation is disabled under `prefers-reduced-motion`.

### The colourway

Taken from *A to Z of The Designers Republic* (Thames & Hudson) — the
orange ground, the near-black graphic, the hot pink accent and the pale
peach. Sampled from the cover, not eyeballed.

| Role | Light | Dark |
|---|---|---|
| ground | `#FFA918` | `#1B262E` |
| ink | `#2F414D` | `#F2A919` |
| pink | `#FD447E` | `#FF6E9C` |
| pale | `#EFD8C9` | `#F5E3D8` |

Dark mode re-grounds the same four on ink rather than orange, so the
mark keeps its contrast instead of glowing on a dark field.

The heart carries the **pink** — it is the only element on the page, so it
is the one that has to read. The favicon is the same heart, still.

## Editing the copy

The copy lives in the HTML. Keep the voice: plain, specific, no hype. If
the sentence would survive being written about any other product, cut it.

Colours and type are CSS custom properties at the top of the file. Light and
dark are both defined; dark follows `prefers-color-scheme`, and the
animation is disabled under `prefers-reduced-motion`.

## Licence

Content © Ian Roberts, CC BY 4.0.
