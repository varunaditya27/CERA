# CERA design contract

Version: 2026-11-16. Branch: `design/research-atlas`.

## Direction

**Scientific editorial.** A serious research publication with one interactive experimental landscape. Precision is the identity. The interface should never resemble a biotech stock template, generic SaaS admin panel, or an AI chatbot wrapper.

## Color tokens (exact)

| Token | Hex | Use |
| --- | --- | --- |
| Deep | `#0E1A1A` | Landing hero and footer |
| Deep secondary | `#17292A` | Results section |
| Ink | `#182722` | Text |
| Paper | `#F2F3EE` | Reading surface |
| Chalk | `#FBFCF8` | High contrast light |
| Muted | `#627169` | Secondary copy |
| Rule | `#D4DBD3` | Dividers |
| Light rule | `#38504C` | Dark dividers |
| Soft | `#E5EAE4` | Hover/background |
| Copper | `#DE966C` | Intervention, primary action |
| Copper soft | `#F2D7C4` | Optional emphasis |
| Mineral | `#A8C8BF` | Scientific visualization |
| Light text | `#F2F3ED` | Text on deep surfaces |
| Light muted | `#ADC2BA` | Supporting text on deep |

No additional colors without purpose and documentation. The visualizations can use transparent derived values for legibility. Color is never the only cue for a status or conclusion.

## Typography

- **Newsreader**, variable serif: all display headings and large data moments. Optical display nature gives a scientific journal feel. Weight 300-400; italic only as deliberate emphasis.
- **Onest**, humanist neo-grotesk: body, navigation, buttons and labels. Weight 400–700. Readability and distinct characters are more important than density.
- **Fragment Mono**, regular: measurements, identifiers, and provenance references. Use sparingly.

Fonts are loaded with Next.js `next/font/google` and self-hosted at build time (`frontend/app/fonts.ts`), using `font-display:swap`. Fallbacks are Georgia, sans-serif and monospace respectively. Do not replace with Inter/Roboto/Space Grotesk/DM Sans or add more font families casually.

## Scale and grid

- Page container: min(100% - 96px, 1320px); 56px under 900px; 40px under 650px.
- Desktop nav: 88px, 72px scrolled; on mobile 72/66px.
- Main sections: 90–154px vertical spacing by density, rather than equal cards.
- Body: 14–16px with 1.65–1.8 line-height.
- Editorial headings: responsive 50–130px, not single fixed sizes.
- Hairline separators: 1px. Default border radius: none.
- Minimum mobile control target: 44px.

## Symbol

Three evidence rails interrupted at the middle by a copper diamond. This refers to a prediction being challenged by an observation, not a synthetic DNA helix. The diamond occupies the central gap, maintaining exact geometry and negative space.

Assets: `frontend/public/cera-symbol.svg`, `cera-wordmark-light.svg`, `cera-wordmark-dark.svg`, `frontend/app/icon.svg`, `frontend/app/opengraph-image.tsx`, React `brand-mark.tsx`.

Keep the symbol readable at 32px. Do not rotate, glow, gradient-fill, or tile it.

## Navigation

Sticky, full-width top bar. On landing it begins transparent, then transitions into the paper reading bar. Other routes use the paper bar immediately. Desktop: symbol/wordmark left, page links centered, GitHub right. Mobile: button-led accessible dropdown. No persistent sidebar, mega-menu, or floating capsule that competes with the research visualization.

## Motion

- Lenis v1.3.27, GSAP v3.15.1. They share GSAP's ticker; GSAP seconds are converted to milliseconds for Lenis.
- Hero entrance: masked three-line headline, followed by description, actions and surface.
- Scroll: restrained section reveals, a subtle hero surface parallax, staged data mark entrances.
- Hover: direct, precise and quick. No custom cursor, random particles, video backgrounds or perpetual decorative animation outside the hero.
- Native touch scrolling and reduced-motion accessibility take precedence.
- Animated graphics are illustrative and must be labeled as such.

## Page structure

Landing page: hero / research question / protocol / dated experimental evidence / protein landscapes / footer.
Dedicated routes: `/datasets`, `/datasets/[id]`, `/experiments`, `/workflow`.
Only the landing page is immersive. Inside routes prioritize reading and comparing.

## Integrity

Do not invent measurement numbers, protein outcomes, warning rates, sources, or claims of successful repairs. The latest comparison is exploratory amylase evidence, not final cross-protein validation. All frozen values should link to their report. If the backend is unavailable, the dataset list may use a visibly labeled committed reference snapshot.

## Accessibility and QA

Semantic headings, tables and navigation; strong focus rings, meaningful alt text, explicit reading order, responsive layouts, adequate contrast, reduced-motion support. A complete release requires mobile and desktop browser verification and a passing Next production build. Never claim these tests succeeded without running them.
