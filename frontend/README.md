# CERA frontend

Next.js 16 / React 19. This branch is a **read-only research presentation**. It does not run the optimization algorithm, accept protein sequences, or modify the saved experiment records.

## Run

```sh
cd frontend
npm ci
npm run dev
# http://localhost:3000
```

To run the connected local dataset catalog, start the separate FastAPI service from the repository root, as documented in the root README. Without the service, the frontend shows explicitly labeled reference counts.

Check the production build with `npm run build`. The design branch also has a frontend build workflow.

## Pages

| Route | Purpose |
| --- | --- |
| `/` | Animated introduction, methodology, measured development findings |
| `/datasets` | Dataset directory |
| `/datasets/[id]` | Provenance, split and caveats |
| `/experiments` | Filterable nine-method amylase comparison |
| `/workflow` | Interactive explanation of the experimental loop |

The results come from `frontend/lib/research.ts`, a frozen source-linked summary of `research/repeated_matched_findings.md`. The graph inside the hero is **conceptual**, not a plot of assay measurements. Dataset source copy lives in `frontend/lib/datasets.ts`.

## Design system

Read [brand/DESIGN.md](../brand/DESIGN.md) and [brand/VOICE.md](../brand/VOICE.md) before making new pages or changes to global styles.

- Newsreader: display typography.
- Onest: readable interface copy.
- Fragment Mono: numeric data.
- CSS tokens in `app/globals.css` define the palette and spatial rhythm.
- Shared top navigation in `components/navigation.tsx` replaces the old sidebar.

## Motion architecture

- `components/motion-runtime.tsx`: Lenis and GSAP use a shared animation clock; touch users and reduced-motion users retain native scrolling.
- `components/landing-motion.tsx`: hero entry, subtle scroll parallax, process and data transitions.
- `components/section-reveal.tsx`: scoped one-time GSAP reveals. Elements are visible without JavaScript and when reduced motion is requested.
- `components/hero-landscape.tsx`: procedural Canvas surface, throttled by visibility with SVG fallback and no hidden assay data.

GSAP animations use scoped contexts and clean up on route changes. Do not add another `requestAnimationFrame` loop to Lenis or stack a second generic animation library for the same interactions.

## Quality checks

Before merging or publishing, confirm these in a real browser:

1. Desktop layouts at 1440px and 1024px, mobile at 390px and 320px, plus a tablet width.
2. Navigation, anchor scrolling, focus outlines, mobile menu (including Escape), and keyboard-only use.
3. Motion on normal devices and still, readable content with `prefers-reduced-motion: reduce`.
4. No horizontal overflow, overlapping hero text, layout jumps, inaccessible comparison tables, or blank content when the backend is offline.
5. Plot values correspond to the committed CSV and source report. Negative repair outcomes must remain explicit.
6. Production build, browser console, accessibility tree and mobile performance.

CI verifies the Next.js build, but does **not** replace browser and visual testing. These visual checks should not be claimed as completed until performed.
