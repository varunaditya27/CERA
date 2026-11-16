# CERA — Visual identity and interface direction

**Working direction:** The Evidence Atlas. Version 1, 16 November 2026. Design work only: scientific method and experimental data remain unchanged.

## Position

CERA studies what happens when a learned reward misleads protein fitness search, and whether carefully checked changes help. Its interface should feel like an instrument used to examine evidence, not a sales website promising a breakthrough.

**Core promise:** Trace every claim to its measurement.
**Primary audience:** project team, researchers, academic reviewers, and technically curious visitors.
**Personality:** precise, inquisitive, measured, quietly expressive.
**Voice:** short, testable statements; plain words for complex concepts; no unsupported victory language.

## Identity concept: a disrupted signal

Three parallel measurement rails. One rail is interrupted by a diamond-shaped observation. The intervention is small, but it changes what the system should do next. It represents a counterexample, not a DNA helix, a generic atom, or an AI sparkle.

The mark is intentionally built from four straight strokes plus one diamond. Use the approved SVG artwork, not an emoji or a rotated collection of UI badges. Preserve generous clearance around the mark and keep details visibly separate at favicon size.

## Palette

| Semantic token | Hex | Purpose |
| --- | --- | --- |
| Dark evidence ink | `#15201D` | Hero, nav, primary text |
| Paper | `#F3F1EB` | Main research canvas |
| Chalk | `#FBFAF6` | Cards, reading surfaces |
| Secondary ink | `#52615B` | Captions and supporting text |
| Rule | `#D9DDD4` | Delineation, not decoration |
| Deep evergreen | `#365D51` | Links, positive structure |
| Signal copper | `#DA925F` | Counterexample / attention accent |
| Soft mint | `#BBD4C7` | Non-semantic hero annotation |

Use copper sparingly. Never rely on copper/green alone to convey the state of research evidence. Avoid purple gradients, neon accents, glassmorphism, meaningless blobs, generic molecule illustrations, and ornamental charts.

## Typography

- **Instrument Serif**: editorial large headings, occasional scientific quotations. No body copy.
- **DM Sans**: navigation, body, data tables and controls.
- **IBM Plex Mono**: dataset IDs, provenance, numerals, timestamps, technical annotations.

Fallbacks are included. Font loading is decorative, not required for function.

## Information architecture

1. **Overview**: the research question, method concept, and evidence orientation.
2. **Landscapes**: source-backed datasets, readiness and split warnings.
3. **Experiments**: clearly dated, frozen development findings from alpha amylase.
4. **Method**: the exact information boundary and the specify/search/audit/repair loop.

The website remains **read-only**. It does not run optimizers. Never show a decorative CTA that implies an experiment can be launched.

## Truthfulness contracts

- `research/experiment-foundations` is the source for the static experiment snapshot.
- Show the date and provenance for any frozen figure.
- Distinguish development results, prepared datasets, and final evaluation.
- Say 'no accepted repairs' instead of implying the system repaired itself.
- Scores are *finite-pool, retrospective* observations, not proof of biological generalization.
- If the backend dataset catalog is offline, show a labeled reference snapshot instead of a broken blank state.

## UI craft

Editorial whitespace and strong text hierarchy, few borders, substantial data hierarchy, no gratuitous grids of feature cards. Every animation conveys transition or focus; respect reduced motion. Minimum 44-pixel tap targets, visible keyboard focus, semantic tables, honest missing states.

## Skill-informed decisions

- **Intent**: explicitly stated audience, task journeys, and information honesty.
- **Hallmark**: structural distinction and avoiding stock AI dashboard motifs.
- **Taste**: typography, proportion, restrained motion and coherent component voice.
- **Brandkit**: a single memorable, geometry-backed symbol applied consistently.
- **Accessibility craft**: focus states, robust fallback content, semantic navigation, reduced-motion behavior.

External references are inspiration, not vendor dependencies. No external skill code or assets are copied into the application.
