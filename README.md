# lastknown.design

The one-pager for [Last Known Voice](https://lastknown.design) — a brand
splash: the mark, the name, one door to the book, and a way to get in touch.

## Structure

| Path | What it is |
|---|---|
| `index.html` | The whole site — markup, CSS and copy in one file |
| `scripts/build-markup.py` | Generates `index.html` from the Pebbles library |
| `pebbles/` | Vendored Pebbles library — geometry (`data.js`) and motion (`styles.js`) |
| `design/` | Comparison sheets used to choose the mark |
| `CNAME` | The custom domain (`lastknown.design`) |
| `.github/workflows/deploy-site.yml` | Copies `index.html` to `_site/` and deploys via the official Pages actions |

## The mark

**Arch**, from the [Pebbles](https://pebbles-showcase.vercel.app/) agent
identity system — a rounded arch body, a tall rounded rect and a circle,
each in its own colour, overlapping.

Geometry, colours and motion are **read from the vendored library** at
build time, not transcribed into the script. `scripts/build-markup.py`
parses `pebbles/data.js` for the character's parts and palette, and
`pebbles/styles.js` for the idle keyframes. If the library changes, the
mark follows it.

```bash
python3 scripts/build-markup.py
```

The character is `Arch`, the colourway is the library's `accent`
palette. Change `CHARACTER` or `PALETTE` at the top of the script to
swap either.

**Dark mode** uses the library's own `paletteDarkVariants` — the same
way the component does it — via a `prefers-color-scheme` media query.

**Motion:** the three parts drift independently on a slow loop while the
whole form breathes. The animation is disabled under
`prefers-reduced-motion`.

### The Pebbles library

`pebbles/` holds `data.js` and `styles.js` from the Pebbles distribution
zip, plus `USAGE.md` (the library's own developer guide). Only the two
files the mark needs are vendored — the component, the morph and the
precomputed contours are not used here.

To refresh from a new distribution:

```bash
curl -sL https://pebbles-showcase.vercel.app/dist/pebbles-assets.zip -o /tmp/pebbles.zip
unzip -o /tmp/pebbles.zip -d /tmp/pebbles
cp /tmp/pebbles/pebbles/data.js /tmp/pebbles/pebbles/styles.js pebbles/
python3 scripts/build-markup.py
```

## Editing the copy

The copy lives in the HTML. Keep the voice: plain, specific, no hype. If
the sentence would survive being written about any other product, cut it.

Colours and type are CSS custom properties at the top of the file. Light and
dark are both defined; dark follows `prefers-color-scheme`, and the
animation is disabled under `prefers-reduced-motion`.

## Licence

Content © Ian Roberts, CC BY 4.0.
