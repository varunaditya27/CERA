# CERA brand system

Working identity, 16 November 2026. Scope: frontend and visual assets only.

## Direction

An editorial research interface. Precise, quiet, and readable.

**Audience:** research team, reviewers, and visitors following the project.

**Content hierarchy:** current results first, context second, detailed methodology through source links. Avoid repeated taglines, uppercase micro-labels, fabricated data graphics, or marketing claims.

## Mark

Three horizontal tracks interrupted at the center by a contrasting diamond. The break represents a counterexample: an observation requiring closer inspection. It remains legible at favicon size.

- Master symbol: `frontend/public/cera-symbol.svg`
- Light and dark horizontal lockups: `frontend/public/cera-wordmark-light.svg`, `frontend/public/cera-wordmark-dark.svg`
- App icon: `frontend/app/icon.svg`
- Social card: `frontend/app/opengraph-image.tsx`
- React mark: `frontend/components/brand-mark.tsx`

Maintain consistent geometry and clear space at least the width of the diamond.

## Colors

| Token | Value | Use |
| --- | --- | --- |
| Ink | `#17251F` | Text |
| Deep | `#101D18` | Navigation and hero |
| Paper | `#F0F2EE` | Main canvas |
| White | `#FAFBF8` | Light contrast |
| Muted | `#53635A` | Supporting content |
| Line | `#D8E0D8` | Separators |
| Copper | `#DE966C` | Intervention and primary action |
| Sage | `#AFC7B8` | Subtle contrast |

**Typography:** Instrument Serif for display headings; DM Sans for interface text; IBM Plex Mono for numerical values.

**Components:** hairline separators, open spacing, minimal surfaces. Motion only for focus and navigation. Respect reduced-motion settings.

## Navigation

- Overview: premise and most important results
- Datasets: landscape profile and provenance
- Results: fixed amylase development study with filtering
- Method: short, accurate explanation of the experiment

The interface is read-only. No experiment execution is exposed to website visitors.

## Integrity

- Frozen results: `research/repeated_matched_findings.md` in `research/experiment-foundations`
- Displayed statistics must match the committed result.
- Do not imply that the existing repair pilot found a successful repair.
- Dataset profile source caveats and split leakage matter; do not conceal them for visual simplicity.
- Offline dataset API uses a visibly disclosed reference snapshot.

## Design review

Apply Hallmark's restraint and anti-template principles, Taste's proportion and typography checks, Intent's user-purpose lens, and Brandkit's coherent identity logic. The result is evaluated by clarity and fidelity, not amount of text or decoration.
