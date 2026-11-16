# CERA / design system

Revised: 16 November 2026. Working branch: `design/research-atlas`.

## Point of view

**An experimental evidence instrument.** Precise enough for a researcher, immediately graspable by someone watching a project demonstration. The visual personality comes from the contrast between **prediction** and **measurement**, not decorative scientific symbols.

The landing page should be curious and memorable. Reading pages should be quiet. There must never be more animation than information.

## Identity / the aperture

The mark is a bespoke open `C` interrupted by an independent copper measurement line. Its unequal elements represent an expectation that is being challenged. This replaces the old rails-and-diamond symbol. The symbol has no dependence on a downloaded font and remains recognizable at small sizes.

Assets:

- `frontend/components/brand-logo.tsx`: inline vector lockup for the navbar
- `frontend/components/brand-mark.tsx`: inline monogram
- `frontend/public/cera-symbol.svg`: standalone mark
- `frontend/public/cera-wordmark-dark.svg` / `cera-wordmark-light.svg`: vector paths, no text-font dependency
- `frontend/app/icon.svg`: favicon
- `frontend/app/opengraph-image.tsx`: social preview

Do not reuse the old diamond. Do not place DNA helices, molecular stock photography, circuitry, hexagonal icons, AI sparkles or generic atom motifs around the mark. Use its opened geometry in focused charts and interactions rather than repeating the logo decoratively.

## Core palette

| Role | Token | Hex |
| --- | --- | --- |
| Deep petrol | `--deep` | `#102425` |
| Deep secondary | `--deep-2` | `#173333` |
| Text | `--ink` | `#182722` |
| Warm paper | `--paper` | `#F3F1EB` |
| Light surface | `--white` | `#FCFCF8` |
| Secondary text | `--muted` | `#596A62` |
| Separator | `--line` | `#D4DBD3` |
| Soft green | `--soft` | `#E5EAE4` |
| Measurement / intervention | `--copper` | `#E9875C` |
| Model / structure | `--sea` | `#9BCDBF` |
| Dark-surface text | `--light-text` | `#F3F1EB` |
| Dark-surface secondary | `--light-muted` | `#ACC6BD` |

Copper on a light background uses the darker `--accent-on-light: #A94828` for readable small text. Do not use color alone to encode a difference: always use names, values, position or status text.

## Typography

- **Geologica**, variable display: designed by Monokrom. Large headings and strong numerals. Use weight 530–650 with variable `SHRP` approximately 38–65 for distinctive technical sharpness. This replaces Newsreader.
- **Onest**, body and interface: comfortable reading, straightforward navigation and controls.
- **Fragment Mono**, tabular figures: measurements, counts, stage numbers and technical reference labels.

All are self-hosted at build time through `next/font/google` in `frontend/app/fonts.ts`. No external font request is needed at runtime. Use one clear display family; do not add a second decorative serif.

## Layout

- Max content width 1320px; desktop side gutters 48px; mobile 20px.
- Desktop top nav: 88px, 72px after scroll. Mobile: 72px, 66px after scroll.
- Landing opens on dark petrol; interior pages use warm paper and an immediately readable top bar.
- Section scale follows content. No arbitrary 3-card grids or repeated slogans to fill space.
- Meaningful line drawings and direct data labels take precedence over rounded cards.

## Routes and presentation flow

1. `/`: question, short interactive prompt, process, current findings, landscapes
2. `/walkthrough`: interactive two-round illustration with reveal/measurement budget and presentation view
3. `/workflow`: the exact research loop and its constraints
4. `/system`: implemented software layers and evidence boundaries
5. `/experiments`: real amylase findings and two-method comparison
6. `/datasets` and `/datasets/[id]`: experimental landscapes, provenance and preparation

Top navigation: custom SVG lockup at left; Walkthrough, Method, Results, Datasets and System at center; GitHub at right. Mobile: responsive button menu. No sidebar.

For a course demonstration, begin with `/`, open the fullscreen `/walkthrough`, then show `/workflow` and `/system`, and finish on `/experiments`. Detailed data questions should link to `/datasets`. Do not add labels like “for faculty” to the public interface.

## Motion

- GSAP and Lenis remain synchronized on a single animation clock.
- Dynamic Canvas surface illustrates a fitness landscape; it is explicitly **conceptual**.
- The 9 vs 3 values in the hero and walkthrough are from the repo's invented teaching example, not real experiment outcomes.
- Scroll reveals and parallax are restrained; touch scrolling remains native; reduced motion disables animated timing.
- Interactive demo controls are explicit, rewindable and keyboard-accessible. Presentation mode enlarges the work area instead of replaying a video.
- Do not add extra animation libraries unless they solve a distinct need.

## Scientific integrity

The current repeated comparison consists of 90 development runs on alpha amylase, not a confirmed scientific improvement. All 120 tested reward-weight proposals were rejected by the current verifier. Neither CERA variant demonstrated an accepted repair. The comparison and its 10 seeds must be clearly identified. Evaluation on IRED and hydrophobic core is not complete. A sourced illustration must never be mistaken for measured evidence.

## Craft gates

Before merging: production build, screenshot review at 1440 / 1024 / 768 / 390 / 320 px, reduced-motion check, mouse and keyboard journey, mobile-menu and presentation-mode checks, correct contrast, no horizontal overflow, source-link and dataset-state verification. The design branch was edited via GitHub; a checked-in workflow does not itself prove the build has passed.
