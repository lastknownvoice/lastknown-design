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

**Huxley** — the 24×24 cellular canvas: X-shaped eyes, a flat mouth, and a
heart at the chest that beats.

Shape and timing come from the Huxley source at `~/dev/huxley/huxley-24.js`.
`scripts/build-markup.py` reads the heart's cell offsets out of it and
lays out the eyes and mouth on the same grid, so the mark is the same
character rather than a redraw.

```bash
python3 scripts/build-markup.py
```

The character is drawn in SVG-in-CSS-grid, so the page stays one static
file — no canvas, no runtime, no JavaScript.

**The beat** is a lub-dub, not a fade: full strength, a drop to half,
a held plateau, then dark. The centre cell of the heart stays dimmer
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

The favicon carries the **heart alone** — at 16px the whole character is
mush, and the heart is the part that reads and the part that beats.

## Editing the copy

The copy lives in the HTML. Keep the voice: plain, specific, no hype. If
the sentence would survive being written about any other product, cut it.

Colours and type are CSS custom properties at the top of the file. Light and
dark are both defined; dark follows `prefers-color-scheme`, and the
animation is disabled under `prefers-reduced-motion`.

## Licence

Content © Ian Roberts, CC BY 4.0.
