# lastknown.design

The one-pager for [Last Known Voice](https://lastknown.design) — the imprint
behind *Conversation Is the Control Layer*.

A single static `index.html`. No build step, no dependencies, no framework.
Push to `main` and GitHub Pages redeploys it.

## Structure

| Path | What it is |
|---|---|
| `index.html` | The whole site — markup, CSS and copy in one file |
| `CNAME` | The custom domain (`lastknown.design`) |
| `.github/workflows/deploy-site.yml` | Builds `_site/` and deploys via the official Pages actions |

## Editing

The copy lives in the HTML. Keep the voice: plain, specific, no hype. If the
sentence would survive being written about any other product, cut it.

Colours and type are CSS custom properties at the top of the file. Light and
dark are both defined; dark follows `prefers-color-scheme`.

## Licence

Content © Ian Roberts, CC BY 4.0.
