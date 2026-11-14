# lastknown.design

The one-pager for [Last Known Voice](https://lastknown.design) — a brand
splash: the mark, the name, one door to the book, and a way to get in touch.

## Structure

| Path | What it is |
|---|---|
| `index.html` | The whole site — markup, CSS and copy in one file |
| `scripts/build-markup.py` | Generates `index.html` from the mark parameters |
| `CNAME` | The custom domain (`lastknown.design`) |
| `.github/workflows/deploy-site.yml` | Copies `index.html` to `_site/` and deploys via the official Pages actions |

## The mark

A 7×7 field of squares with a pulse travelling outward from the centre —
a voice radiating. The vignette falls off toward the corners so the shape
reads as a solid square at rest, and the pulse is a highlight travelling
over a shape that already exists.

Tune it in `scripts/build-markup.py`:

```python
FLOOR   = 0.22   # corner cells at rest
PEAK    = 0.62   # centre cells at rest
FALLOFF = 0.062  # per unit of distance
```

Then `python3 scripts/build-markup.py` and push.

**One rule worth keeping:** `grid-column: calc(var(--x) + 4)` does not work.
`grid-column-start` needs a plain integer, and `calc()` over a custom
property holding a unitless number is not accepted as one. Write the final
1-based position into the markup as `grid-area:<row>/<col>` instead.

## Editing the copy

The copy lives in the HTML. Keep the voice: plain, specific, no hype. If
the sentence would survive being written about any other product, cut it.

Colours and type are CSS custom properties at the top of the file. Light and
dark are both defined; dark follows `prefers-color-scheme`, and the
animation is disabled under `prefers-reduced-motion`.

## Licence

Content © Ian Roberts, CC BY 4.0.
