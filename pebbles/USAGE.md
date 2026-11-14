# Using Pebbles

Pebbles is a framework-neutral Web Component and a pure SVG helper. There are no runtime dependencies or required build tools. Serve ES modules over HTTP; opening module files with `file://` is not supported by browsers.

Copy `src/` into your app as `pebbles/`, or use the `pebbles/` folder in the downloadable library ZIP. Keep its files together so the optional dynamic morph import resolves.

```html
<script type="module" src="./pebbles/element.js"></script>
<pebble-agent character="Pip" state="working" size="64" theme="light"></pebble-agent>
```

## Settings

| Attribute | Values | Default |
| --- | --- | --- |
| `character` | Arch, Pip, Block, Orbit, Offset (case insensitive) | Arch |
| `state` | still, idle, waiting, working, listening, success, failure, assemble, disassemble | idle |
| `palette` | bold, accent, duo, g2, contrast | bold |
| `theme` | light, dark; chooses pigments, not the surrounding background | light |
| `size` | 16–512 pixels; use 48+ for animated production identities | 192 |
| `speed` | 0.25–3; 1 is normal speed | 1 |
| `intensity` | 0–2; modifies movement amplitude | 1 |
| `motion` | auto, reduced; the OS preference always takes priority | auto |
| `interactive` | Boolean: presence enables hover and click/keyboard reactions | absent |
| `paused` | Boolean: presence freezes playback | absent |
| `label` | Optional accessible label | character name / replay action |

Boolean HTML attributes are enabled by presence: use `removeAttribute('paused')`, not `paused="false"`.

```js
import './pebbles/element.js';
const agent = document.createElement('pebble-agent');
agent.configure({ character: 'Arch', state: 'listening', size: 64 });
document.querySelector('#agent').append(agent);
agent.pause();
agent.play();
agent.replay();
await agent.morphTo('Pip', { duration: 650 });
```

`morphTo` loads its module and precomputed contours on demand. A new morph continues from the current rendered geometry. Its promise resolves `true` when completed and `false` when superseded or disconnected. Duration is in milliseconds before speed scaling. Reduced-motion users see the target directly. Morphs and CSS motion pause while hidden, offscreen or explicitly paused. In a paused morph, call `play()` before awaiting completion.

One-off states retain their final frame. Disassemble runs assembly backwards over 1.4 seconds at speed 1 and ends invisible. Call `replay()` or change `state` to show another behaviour. Idle click reactions are staggered ripples; hover wakes the outer form. `interactive` adds keyboard focus and Enter/Space activation.

## Static SVG and presets

The core helper has no DOM dependency, so it can run during server rendering or a build:

```js
import { renderSVG, serializePreset, parsePreset } from './pebbles/core.js';
const svg = renderSVG({ character: 'Pip', palette: 'bold', theme: 'dark', size: 64 });
const json = serializePreset({ character: 'Pip', state: 'working' });
const settings = parsePreset(json);
```

An SVG is a still identity, not an animation recording. Presets store component settings; they do not package the runtime. Exported previews and code use the same definitions and normalisation. The current showcase remains a self-contained reference; the new playground uses the library.

## Performance and accessibility

- Three SVG geometry elements for ordinary identities; transform/opacity CSS motion needs no per-frame application JavaScript.
- One constructed stylesheet and shared visibility/resize observers across component instances (a style-tag fallback covers older browsers).
- Optional morph code is absent from the initial component dependency graph. Contours are generated ahead of time; clients interpolate 128 points per shape only while morphing.
- Visibility changes pause playback; disconnecting cleans observers and pending morphs.
- System reduced-motion preferences cannot be overridden to force animation. Decorative placements should receive an appropriate accessible label or be hidden by the containing UI when redundant.
- Size is the SVG viewport, including the identity’s original surrounding space. Optical amplitude increases slightly at small sizes, independently of geometry.

Run `npm test` for data/export safety checks, `npm run build` for distributable modules and measured gzip sizes, and `npm run package` for the library ZIP. The size report sums separately compressed ES modules; it is not a claim about browser memory, frame rate or end-to-end transfer overhead. Runtime compatibility: current browsers supporting custom elements, Shadow DOM, ResizeObserver and IntersectionObserver. TypeScript declarations are included.

## Distribution status

This is a source package in a private repository, not a published npm package. No open-source licence has been assigned. The repository’s existing publication and branding guidance still applies.
