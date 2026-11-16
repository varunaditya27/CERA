# CERA frontend

Next.js 16 + React 19. The research website is **read-only**. It explains and displays the existing project, without running optimization or revealing hidden assay labels.

## Run

```sh
cd frontend
npm ci
npm run dev
# http://localhost:3000
```

Start the FastAPI dataset catalog separately using the root README. Without it, the website uses visibly labeled committed reference counts. For a production build run `npm run build`.

## Routes

| Route | Function |
| --- | --- |
| `/` | Question, visual example, method, real development findings |
| `/walkthrough` | Hands-on, four-step **illustrative** experiment with presentation view |
| `/workflow` | Interactive breakdown of the method and protocol |
| `/system` | Software architecture and scientific boundaries |
| `/experiments` | Frozen 90-run amylase findings, table and two-method comparison |
| `/datasets` | Dataset directory |
| `/datasets/[id]` | Dataset provenance and preparation notes |

## Research integrity

The 9-to-3 example on the landing page and in `/walkthrough` is **invented for teaching**, drawn from `research/experiment_walkthrough.md`. It must never be presented as an observed amylase result.

The experiment data displayed in `/experiments` comes from `frontend/lib/research.ts`, a frozen, linked summary of `research/repeated_matched_findings.md`. The model-assisted repair study did **not** accept any changes. IRED and Hydro evaluations are pending.

## Identity and design

Read [design system](../brand/DESIGN.md), [voice](../brand/VOICE.md), and [design references](../brand/INSPIRATION.md).

- Custom open-C aperture symbol and geometric CERA vector lockup. Assets live in `public/`, `app/icon.svg` and `components/brand-logo.tsx`.
- **Geologica** with a loaded Sharpness axis for headlines; **Onest** for interface; **Fragment Mono** for values.
- `next/font/google` self-hosts the font assets at build time.
- Petrol, warm paper, mineral green, and copper, defined as CSS variables in `app/globals.css`.
- Responsive sticky top nav, not a permanent sidebar.

## Motion

- `components/motion-runtime.tsx` runs GSAP and Lenis on one clock.
- `components/landing-motion.tsx` stages the entrance and scroll-linked sections.
- `components/hero-landscape.tsx` is a procedural illustration, not experimental data. It has a static SVG fallback.
- `components/section-reveal.tsx` uses scoped GSAP with cleanup and keeps content readable if JavaScript or motion is unavailable.
- Mobile coarse pointers scroll natively; reduced-motion preferences are respected.

## Suggested demonstration

`Home → Walkthrough (Present) → Method → System → Results`, then open a dataset profile if requested.

The illustrative walkthrough is deliberately separate from measured results. The System page shows the implementation boundary, while Results shows what succeeded or failed in actual experiments. This distinction is more important than a glossy transition.

## Quality gates

Before merging:

- `npm ci && npm run build` from `frontend/`, checked in CI.
- Browser inspection at 1440, 1024, 768, 390 and 320 px.
- Click and keyboard checks for all navigation links, the walkthrough's steps, Back/Reset and presentation mode, method tabs, and comparison selects.
- Contrast and accessible labels, including a reduced-motion run.
- No clipped hero words or horizontal page overflow.
- Research values, early-stop accounting and citations cross-checked against the saved report.
- Evaluate any performance loss from Canvas/GSAP/Lenis on a lower-powered device.

CI does not replace actual browser checks. These checks should not be reported as passed unless they were run.
