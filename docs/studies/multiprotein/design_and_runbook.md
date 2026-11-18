<div align="center">

# Multi-protein study design and runbook

Design notes

</div>

## Evaluation options

This document is a proposal for review. It does not freeze a final protocol, modify code or report search results for IRED or the hydrophobic-core proteins.

### Goal and current capability

The project needs to compare its repair approach against simpler search methods on proteins other than the amylase data used for development. Each method must begin with the same measured examples for a given protein and seed, use the same eligible pool, mutation limit and maximum measurement budget, and report early stops and actual costs. A seed is a number used to reproduce random choices. The three hydrophobic-core proteins must be analyzed separately because they have different sequences and score scales.

The current predictor pilot supports IRED and each hydrophobic-core protein. The existing repeated comparison and random baseline are hard-wired to amylase, and the existing audits and recovery summaries must be checked for their assumptions before reuse. Therefore, running the complete matched comparison requires implementation and tests; simply passing another dataset name to the existing repeated script is not enough. Existing raw files include all scores, so this is an information boundary in the experiment interface, not a security boundary.

### Starting-example choice

The benchmark supplies a train/test split. In IRED, its split is based on number of changes from the reference sequence. In the hydrophobic-core low-to-high split, the train/test assignment is based on the measured scores. If the experiment chooses starting examples from the train side of the latter split, the choice already contains information about scores even when the search code does not read unseen scores.

1. **Score-blind starting examples (recommended primary protocol).** Sample initial measurements from all eligible variants without consulting the train/test or validation flags, and keep all other eligible variants as candidates. This better models a search without advance score knowledge and avoids leaking score-derived Hydro split membership. It does not reproduce the benchmark's original train/test task, and it changes the starting distribution relative to the earlier amylase development comparisons. Every method must share exactly the same initial set, and the result must be called a retrospective finite-pool search, not an official FLIP2 benchmark score.
2. **Original train-side starting examples.** Sample from the published train side, as in the current runner. This is easier to compare with the prior development setup and preserves the benchmark's split membership in the starting data. For Hydro it uses privileged score-derived membership, and its results should not be described as score-blind. It may still be useful as a separately labeled sensitivity analysis, subject to a fixed protocol.

The official [FLIP2 description](https://flip.protein.properties/) identifies the original split designs; the local [Hydro preparation](../../data/hydro_preparation.md) documents the score-derived split. Neither choice guarantees unbiased estimates of real-world protein engineering performance, and IRED's local file covers only a subset of the screened variants.

### Feasibility check

With the existing four-substitution limit, IRED has 7,633 eligible variants and the three Hydro groups have 1,010, 1,292 and 2,916. After 100 starting measurements, each group would still have more than the planned maximum of 100 new measurements available. These are sequence-eligibility counts, not search results. For a score-blind implementation, sort the eligible sequence identifiers before seeded sampling and test invariance to CSV row order as well as split flags; this makes the sampled set reproducible even if file rows are reordered.

### Proposed implementation steps if score-blind starts are selected

1. Add a clearly specified starting-pool choice to the existing controlled measurement runner, retaining the current default for historical reproducibility. Independently test that the score-blind choice does not depend on split or validation flags, that every method receives identical initial observations, and that budget and duplicate-query checks still hold.
2. Extend the random baseline and a matched comparison runner to dispatch the four protein groups, recording dataset and source fingerprints, the starting rule, seeds, methods and failure or early-stop statuses. Exercise the workflow using synthetic datasets before running evaluation-protein searches. Keep source files and existing run records unchanged.
3. Before interpreting evaluation results, write and review a complete frozen protocol: methods and opt-in repair settings, seeds, predictor and calibration roles, budgets, primary comparison, recovery rule, reporting of incomplete follow-up, Gemini use and costs, and audit procedure. Run the planned matched comparisons only under that reviewed protocol.

This plan describes the implementation direction, not a completed study. A chosen starting-pool rule alone does not settle the final set of methods or the scientific merit of current warning and repair checks.

## Comparison protocol draft

Status: **approved for execution on 17 November 2026**, after the documented pre-study review corrections; this is not a completed evaluation. No IRED or hydrophobic-core search outcome has been used to select these settings. Dataset provenance work and score-file matching were performed earlier, so these datasets must not be described as completely unseen to the project.

### Question

On the available measured variants, how do the experimental warning-and-repair search methods compare with fixed reward and simpler alternatives when each method starts with the same observations and has the same maximum measurement budget? A run is a retrospective search through a finite set of variants with already recorded measurements. It is not a laboratory experiment or an official FLIP2 benchmark evaluation.

### Approved scope

- Analyze IRED, Hydro P06241, Hydro P01053 and Hydro P0A9X9 as four separate protein groups. The original Hydro score-derived split is not used to choose initial observations. IRED represents a subset of screened variants; the exact filtering is unresolved.
- Use ten matched seeds, 51–60, for every protein and method. For each seed sample 100 initial variants from sorted identifiers of all eligible sequences, ignoring benchmark split and validation flags. Permit at most four substitutions relative to the appropriate reference and at most 100 additional measurements in batches of at most ten. Each method must receive the same initial variants and scores for that seed and protein.
- Match model-role and predictor-member seeds across predictor-based methods, using the existing `2000 + seed` and `3000 + seed` assignments. The 20 reserved starting measurements set prediction ranges; the others and later measurements fit the predictors. Record the Python version, checkpoint, cache, data, code, model and dependency fingerprints. Random search does not fit a predictor.
- Primary comparison: fixed reward, rule-based repair and Gemini-assisted repair. Use the existing checked example reward specification. For both repair methods enable the approved targeted-disagreement and direct-diversity checks. Gemini chooses only among a finite sanitized menu and the normal verifier still decides acceptance; failures use the documented fallback and must be counted. Gemini calls may incur charges or encounter project-specific rate limits; report request attempts, fallbacks, reported tokens and observed charges if available, without inventing a price. [Google's rate-limit documentation](https://ai.google.dev/gemini-api/docs/rate-limits) says limits depend on the project and model.
- Additional comparisons: random search, greedy prediction, mean-plus-spread, Gaussian expected improvement, finite-pool recombination and AdaLead-style search. These are the existing implementations. In particular, expected improvement using ensemble spread is an approximation, not a claim to implement a complete Bayesian optimization system; local-search methods are constrained to the finite measured pool.

This full list is nine methods × ten seeds × four proteins = 360 attempted runs. It could take substantial time and storage; the existing 90-run amylase comparison occupied approximately 219 MiB, but protein sizes and early stops differ, so that is not a reliable forecast for this study. The configured Gemini model's actual quota and cost have not been established here.

### Provider pricing check (17 November 2026)

The locally configured model name is `gemini-3.5-flash-lite`; Google lists that name as a [stable model](https://ai.google.dev/gemini-api/docs/models/gemini-3.5-flash-lite). Google's [standard pricing page](https://ai.google.dev/gemini-api/docs/pricing) lists a free tier and paid rates of USD 0.30 per million input tokens and USD 2.50 per million output tokens, including thinking tokens, at the time of this check. The actual account tier, available quota, exact number of future calls and final charges were not checked and must not be inferred from these list prices. Prices and model availability can change. The existing advisor sends warning types and sanitized menu metadata; it does not send sequences or fitness scores. No request was made for this pricing check.

#### Provider-response accounting caveat

The current client sets `maxOutputTokens` to 2,048 and treats responses whose finish reason is not `STOP` as invalid. Google's [thinking documentation](https://ai.google.dev/gemini-api/docs/thinking) says this limit includes both reasoning and visible output, so truncation is possible even for a short requested answer. The advisor records invalid responses and may retry or fall back, but the client currently discards usage metadata when it rejects a response before returning it. Consequently, the recorded token sum can omit usage from rejected responses and must not be described as total billed usage or used alone to calculate actual charges. The account's billing records would be needed for a complete cost check. This is a code-and-documentation review, not a live test of the configured account.

### Outcomes and reporting

The primary outcome is best observed score at each method's actual stop, paired by protein and seed, together with the number of new measurements. This compares complete policies under the same upper budget; it must not disguise an early stop as a 100-measurement result. Also report the per-run best-score curve, feasible-pool regret, and top-1% indicator, noting whether the starting set already achieved the latter. The eligible-pool optimum and top-1% threshold may be calculated only by an evaluator after all planned selectors have finished; neither is passed back to search.

For predictor methods report recorded range coverage, its numerator and denominator, and mean width. For the first coverage warning report the approved recovery summary: the first subsequent 30-measurement window with 26–28 covered scores, or no warning, insufficient follow-up, or no observed recovery. Report stop reason, unspent budget, warning counts, repair attempts and accepted changes, model calls and failures. Recovery is descriptive and is not proof that a repair caused a change. Random search has no prediction ranges; report these fields as unavailable, not zero.

Keep failed, interrupted and early-stopped runs visible. For each protein show every seed and paired difference; do not pool raw scores across proteins or treat the ten seeds as ten independent biological datasets. No confidence or significance claim is prespecified here; the modest number of proteins and shared source data substantially limit generalization. Any later inferential method needs its own stated assumptions and a separate review.

### Before any evaluation-protein runs

1. Implement and test an evaluator for score-blind starting sets and all four protein groups. It must verify source and run fingerprints, method and seed settings, the deterministic starting sample, matching initial observations, measurement chronology and budget, scores, stop reason and output denominators. It must wait until every configured run has a terminal status before reading full-pool scores. Test valid and deliberately altered synthetic records, including failed and interrupted runs.
2. Independently audit representative reconstructed candidate selections, repair replays and pre-reveal warning evidence; specify what the audit does not refit or verify. Preserve original records and retain all failures. Complete the synthetic end-to-end workflow before using evaluation-protein outcomes.
3. Review the final method list, chosen repair modes, treatment of failures, output locations and provider quota/cost information. Freeze the protocol and implementation before running the real comparison. If any step or setting changes after viewing results, mark subsequent analyses as exploratory rather than treating them as the originally planned evaluation.

This draft does not claim that existing warnings identify true failures or that repair checks prove later benefit. It also does not claim that the present score-blind runner or evaluator has been scientifically validated merely because its software tests pass.

## Runbook draft

Varun approved this execution plan on 17 November 2026, subject to the documented pre-study review corrections. It implements the [comparison draft](design_and_runbook.md#comparison-protocol-draft) with the full nine-method scope selected by Varun. No output paths below existed when checked on 17 November 2026. The IRED and three Hydro representation cache fingerprints matched their recorded pins in that check. Recheck paths, free space, model availability, account quota and pricing immediately before execution.

Run the following as four separate commands from the repository root, using the same checked-out code, specification and Python environment throughout. They create new directories and do not evaluate the full pool:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend:. python3 -m scripts.multiprotein.run_matched_proteins output/multiprotein/four_protein/matched_eval_51_60_ired --dataset ired --seeds 51 52 53 54 55 56 57 58 59 60 --methods random greedy fixed repair gemini_repair ucb ei genetic adalead --specification configs/reward_spec_example.json --targeted-disagreement --direct-diversity
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend:. python3 -m scripts.multiprotein.run_matched_proteins output/multiprotein/four_protein/matched_eval_51_60_hydro-P06241 --dataset hydro-P06241 --seeds 51 52 53 54 55 56 57 58 59 60 --methods random greedy fixed repair gemini_repair ucb ei genetic adalead --specification configs/reward_spec_example.json --targeted-disagreement --direct-diversity
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend:. python3 -m scripts.multiprotein.run_matched_proteins output/multiprotein/four_protein/matched_eval_51_60_hydro-P01053 --dataset hydro-P01053 --seeds 51 52 53 54 55 56 57 58 59 60 --methods random greedy fixed repair gemini_repair ucb ei genetic adalead --specification configs/reward_spec_example.json --targeted-disagreement --direct-diversity
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend:. python3 -m scripts.multiprotein.run_matched_proteins output/multiprotein/four_protein/matched_eval_51_60_hydro-P0A9X9 --dataset hydro-P0A9X9 --seeds 51 52 53 54 55 56 57 58 59 60 --methods random greedy fixed repair gemini_repair ucb ei genetic adalead --specification configs/reward_spec_example.json --targeted-disagreement --direct-diversity
```

The Gemini method can make hosted requests and may incur charges. The advisor receives warning types and sanitized menu information, not sequences or scores. Preserve provider failures and fallbacks. A run may fail, stop early, exhaust its budget or have no permitted neighbors; none should be silently replaced. Resume uses the same full command with `--resume`, checks inputs and completed-record fingerprints, and does not retry failed or interrupted runs. Investigate partial or failed work without overwriting its records.

After **all four groups** have terminal statuses, audit their saved decisions and only then evaluate all four together:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend:. python3 -m scripts.multiprotein.audit_matched_proteins output/multiprotein/four_protein/matched_eval_51_60_ired output/multiprotein/four_protein/matched_eval_51_60_hydro-P06241 output/multiprotein/four_protein/matched_eval_51_60_hydro-P01053 output/multiprotein/four_protein/matched_eval_51_60_hydro-P0A9X9
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend:. python3 -m scripts.multiprotein.evaluate_matched_proteins output/multiprotein/four_protein/matched_eval_51_60_report.json output/multiprotein/four_protein/matched_eval_51_60_ired output/multiprotein/four_protein/matched_eval_51_60_hydro-P06241 output/multiprotein/four_protein/matched_eval_51_60_hydro-P01053 output/multiprotein/four_protein/matched_eval_51_60_hydro-P0A9X9 --specification configs/reward_spec_example.json
```

The audit reconstructs decisions from saved predictions, plus representative sequence-proposal and distance checks; it does not refit predictors or validate scientific assumptions. The evaluator preserves missing comparisons for failed/interrupted runs, reports actual stops and the approved recovery summaries, and does not overwrite an existing report. Both normally require all four groups to be terminal. Results must be reported separately by protein, including unsuccessful runs and all limitations in the draft protocol.

Software preflight so far: 92 backend tests passed, including synthetic nine-method IRED-format and two-method Hydro-format workflows, terminal-status and altered-record checks. The model service and full multi-protein workload were not exercised by those tests. A formal independent two-axis branch review has not been completed.

## Code review

Reviewed the changes from `e5a3cc4` through `6335ea1` on 17 November 2026, using the two-axis `mattpocock-skills:code-review` workflow and the [comparison draft](design_and_runbook.md#comparison-protocol-draft) as the specification. The two review axes were conducted independently. Findings are based on code inspection; no real protein searches were run for this review.

### Standards

- The evaluator accepts an empty or incomplete recorded source-fingerprint map, weakening the provenance check for altered or damaged records. See `backend/app/analysis/multiprotein_evaluation.py`.
- The evaluator and independent audit decompress run files before checking their compressed fingerprints. A corrupted file can therefore consume substantial resources before rejection. Checking the compressed fingerprint first does not protect against a deliberately replaced file and matching fingerprint, so this is a limited integrity improvement rather than a complete defense.
- Judgment call: the audit function is long and handles several separate checks, making it harder to review. Some independent duplication is intentional because the audit should not reproduce a selector's implementation.
- Judgment call: normal-mode entry points accept four groups with matching but incomplete seed or method lists. The documented runbook supplies the intended scope, but the output label alone does not prove the complete approved study ran.

### Spec

- **Cross-protein settings are not fully matched.** The runbook requires the same code and Python environment, but the evaluator and audit compare only seeds, methods, repair flags and reward-specification hash. A different code version, dependency version or Gemini model could be combined into one report. Dataset, reference and cache fingerprints legitimately differ by protein and should be checked within each group, not equated across groups.
- **The approved study scope is not enforced.** Normal four-protein evaluation accepts any matching nonempty lists of seeds and methods, even though the approved draft specifies seeds 51–60 and nine methods. A reduced study can receive the `four_protein` scope label.
- **Fingerprint and cost reporting are incomplete.** The evaluator checks only source-fingerprint entries that are present, so an empty map passes. It also reports repair counts but omits per-attempt repair costs required in the [roadmap](../../overview/roadmap.md). These costs are dimensionless rule-change costs, not provider charges.

### Proposed corrections before real runs

1. In both normal-mode entry points, verify the approved seeds, nine-method list and two repair flags, and require identical implementation, Python/dependency versions and Gemini model across groups. Preserve an explicitly labeled partial development mode.
2. Require the complete expected set of recorded predictor source fingerprints and compare each with its manifest. Check compressed fingerprints before decompression, then verify uncompressed fingerprints.
3. Report the recorded cost for every proposed repair and identify which proposed repair was accepted. The existing cost is `(new weight − old weight) / (allowed maximum − allowed minimum) + 0.05`; for example, raising a weight from 0.50 to 0.75 in a 0–2 range costs 0.175. This is a dimensionless rule-change score used to order options, not money or compute time. Keep it separate from Gemini token usage or financial charges, and do not infer unrecorded usage.
4. Test mismatched group manifests, reduced scope, missing source entries, invalid compressed fingerprints and cost reporting on synthetic records, then rerun the full backend suite. Do not start the real study until the corrections pass.

### Corrections and rechecks

With Varun's approval, normal-mode evaluation and audit now require all four groups, seeds 51–60, the nine agreed methods, both agreed repair options and the approved example specification fingerprint. Group manifests must also agree on code, Python, dependencies and Gemini model. Dataset-specific input and cache fingerprints remain separate. Both paths require the complete recorded predictor source list and check compressed fingerprints before decompression. The evaluator reports each recorded rule-change cost and acceptance; the audit independently checks its allowed menu value, cost formula, attempt order and fallback choice. Synthetic tests cover scope, mismatched settings, incomplete source lists, altered costs, record corruption and preserved failures. The full backend suite passed 97 tests. These checks do not establish scientific validity or guard against every form of deliberate tampering.

Counts: two documented-standard concerns and two judgment calls; the most consequential standard concern is incomplete source verification. Three spec findings; the most consequential is that different code or models can be silently combined across proteins.
