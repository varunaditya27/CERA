# Draft multi-protein comparison protocol

Status: **proposal for review**, not a frozen protocol or completed evaluation. No IRED or hydrophobic-core search outcome has been used to select these settings. Dataset provenance work and score-file matching were performed earlier, so these datasets must not be described as completely unseen to the project.

## Question

On the available measured variants, how do the experimental warning-and-repair search methods compare with fixed reward and simpler alternatives when each method starts with the same observations and has the same maximum measurement budget? A run is a retrospective search through a finite set of variants with already recorded measurements. It is not a laboratory experiment or an official FLIP2 benchmark evaluation.

## Proposed scope

- Analyze IRED, Hydro P06241, Hydro P01053 and Hydro P0A9X9 as four separate protein groups. The original Hydro score-derived split is not used to choose initial observations. IRED represents a subset of screened variants; the exact filtering is unresolved.
- Use ten matched seeds, 51–60, for every protein and method. For each seed sample 100 initial variants from sorted identifiers of all eligible sequences, ignoring benchmark split and validation flags. Permit at most four substitutions relative to the appropriate reference and at most 100 additional measurements in batches of at most ten. Each method must receive the same initial variants and scores for that seed and protein.
- Match model-role and predictor-member seeds across predictor-based methods, using the existing `2000 + seed` and `3000 + seed` assignments. The 20 reserved starting measurements set prediction ranges; the others and later measurements fit the predictors. Record the Python version, checkpoint, cache, data, code, model and dependency fingerprints. Random search does not fit a predictor.
- Primary comparison: fixed reward, rule-based repair and Gemini-assisted repair. Use the existing checked example reward specification. For both repair methods enable the approved targeted-disagreement and direct-diversity checks. Gemini chooses only among a finite sanitized menu and the normal verifier still decides acceptance; failures use the documented fallback and must be counted. Gemini calls may incur charges or encounter project-specific rate limits; report request attempts, fallbacks, reported tokens and observed charges if available, without inventing a price. [Google's rate-limit documentation](https://ai.google.dev/gemini-api/docs/rate-limits) says limits depend on the project and model.
- Additional comparisons: random search, greedy prediction, mean-plus-spread, Gaussian expected improvement, finite-pool recombination and AdaLead-style search. These are the existing implementations. In particular, expected improvement using ensemble spread is an approximation, not a claim to implement a complete Bayesian optimization system; local-search methods are constrained to the finite measured pool.

This full list is nine methods × ten seeds × four proteins = 360 attempted runs. It could take substantial time and storage; the existing 90-run amylase comparison occupied approximately 219 MiB, but protein sizes and early stops differ, so that is not a reliable forecast for this study. The configured Gemini model's actual quota and cost have not been established here.

## Provider pricing check (17 November 2026)

The locally configured model name is `gemini-3.5-flash-lite`; Google lists that name as a [stable model](https://ai.google.dev/gemini-api/docs/models/gemini-3.5-flash-lite). Google's [standard pricing page](https://ai.google.dev/gemini-api/docs/pricing) lists a free tier and paid rates of USD 0.30 per million input tokens and USD 2.50 per million output tokens, including thinking tokens, at the time of this check. The actual account tier, available quota, exact number of future calls and final charges were not checked and must not be inferred from these list prices. Prices and model availability can change. The existing advisor sends warning types and sanitized menu metadata; it does not send sequences or fitness scores. No request was made for this pricing check.

## Outcomes and reporting

The primary outcome is best observed score at each method's actual stop, paired by protein and seed, together with the number of new measurements. This compares complete policies under the same upper budget; it must not disguise an early stop as a 100-measurement result. Also report the per-run best-score curve, feasible-pool regret, and top-1% indicator, noting whether the starting set already achieved the latter. The eligible-pool optimum and top-1% threshold may be calculated only by an evaluator after all planned selectors have finished; neither is passed back to search.

For predictor methods report recorded range coverage, its numerator and denominator, and mean width. For the first coverage warning report the approved recovery summary: the first subsequent 30-measurement window with 26–28 covered scores, or no warning, insufficient follow-up, or no observed recovery. Report stop reason, unspent budget, warning counts, repair attempts and accepted changes, model calls and failures. Recovery is descriptive and is not proof that a repair caused a change. Random search has no prediction ranges; report these fields as unavailable, not zero.

Keep failed, interrupted and early-stopped runs visible. For each protein show every seed and paired difference; do not pool raw scores across proteins or treat the ten seeds as ten independent biological datasets. No confidence or significance claim is prespecified here; the modest number of proteins and shared source data substantially limit generalization. Any later inferential method needs its own stated assumptions and a separate review.

## Before any evaluation-protein runs

1. Implement and test an evaluator for score-blind starting sets and all four protein groups. It must verify source and run fingerprints, method and seed settings, the deterministic starting sample, matching initial observations, measurement chronology and budget, scores, stop reason and output denominators. It must wait until every configured run has a terminal status before reading full-pool scores. Test valid and deliberately altered synthetic records, including failed and interrupted runs.
2. Independently audit representative reconstructed candidate selections, repair replays and pre-reveal warning evidence; specify what the audit does not refit or verify. Preserve original records and retain all failures. Complete the synthetic end-to-end workflow before using evaluation-protein outcomes.
3. Review the final method list, chosen repair modes, treatment of failures, output locations and provider quota/cost information. Freeze the protocol and implementation before running the real comparison. If any step or setting changes after viewing results, mark subsequent analyses as exploratory rather than treating them as the originally planned evaluation.

This draft does not claim that existing warnings identify true failures or that repair checks prove later benefit. It also does not claim that the present score-blind runner or evaluator has been scientifically validated merely because its software tests pass.
