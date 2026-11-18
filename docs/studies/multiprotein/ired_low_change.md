<div align="center">

# IRED low-change start

Plan, runbook and findings

</div>

## Plan

Status: draft for review, 17 November 2026. Varun chose to start with variants that have at most two changes and then allow all eligible unmeasured variants as candidates. This choice does not by itself establish a completed study. The IRED outcomes from the earlier comparison have already been inspected; additional runs are exploratory and do not constitute independent validation.

### Question and candidate settings

Can the compared policies find strong measured variants when starting from lower-mutation IRED variants but free to choose any eligible variant afterward? The [FLIP2 description](https://flip.protein.properties/) defines its IRED split by mutation count, but this study permits later measurement and retraining on either side, so it is a sequential-search adaptation rather than the official static benchmark.

Proposed: reuse the prior nine methods and reward specification, ten matched seeds 61–70, 100 initial measurements, at most 100 additional measurements, batches of ten, and the four-substitution limit. The benchmark's train pool contains variants with zero to two substitutions; use its eligible rows including those flagged for benchmark validation, consistent with the previously approved development protocol. The experiment makes its own score-independent assignment of 20 of the 100 initial measurements to prediction-range calibration. A calibration set adjusts ranges; it does not prove their future accuracy. Initial sampling uses the loader's recorded train-row order, as the existing `Experiment` implementation does, and the audit must reproduce that exact order.

All methods receive the same starting observations for each seed and access to all eligible unmeasured sequences without their scores. Record the number of substitutions for each selection, actual measurement counts, early stops, fixed-versus-repair paired outcomes, and range coverage. A run can remain in the low-change pool throughout, so do not claim that it crossed the boundary without measuring its selections. Compute full-pool outcome references only after every planned run has a terminal status. Keep proteins and score scales separate.

The prior comparison used Gemini and incurred provider calls. This proposal includes the same Gemini-assisted method, so new calls may incur charges; exact quota and billing are unknown. No provider request or new protein-search run has been made under this draft.

### Implementation and checks proposed for approval

1. Extend the matched runner to explicitly record and pass the selected initial-pool mode. Limit the new low-change mode to IRED so Hydro's score-derived train membership cannot silently enter this study. Keep the previous all-eligible mode and its exact verification contract.
2. Extend the evaluator and independent audit to reconstruct the ordered IRED starting pool, verify matched starts, input fingerprints and all-eligible candidate access, and count selected variants by substitution count. Keep output directories and study identity separate from the completed four-protein study; reject changed manifests on resume.
3. Test synthetic IRED records for the selected start and candidate rules, matched methods, validation-flag handling, fingerprint and start tampering, insufficient eligible starts, score hiding, failed or interrupted records, and preservation of the old all-eligible study checks. Run the backend test suite and independently review the changes before any real search.
4. Freeze a runbook with exact methods, seeds, output location, audit and failure handling. Only then run the reviewed study, independently audit the saved records, evaluate all methods after terminal statuses, and document limitations and actual API calls.

These are proposed steps. They do not establish a causal repair effect or recover the originally proposed test-only shift comparison. Unknowns include whether local-search methods have suitable neighbors and how often a policy actually selects a more-changed sequence. Those are outcomes to report, not settings to tune after looking at results. The [scikit-learn guidance on leakage](https://scikit-learn.org/stable/common_pitfalls.html#data-leakage) explains why information unavailable at selection time must not influence model construction; this retrospective sequential design intentionally permits measurements to be used after they have been revealed.

### Starting-pool preflight

A read-only check independently reconstructed the loader's ordered train identifiers from the CSV's sequence, split and validation fields and the reference, then matched all 4,408 identifiers and verified that each has at most two substitutions. Sampling 100 identifiers with each proposed seed 61–70 produced 100 unique members of that pool. Between 13 and 20 sampled identifiers per seed carried the benchmark's validation flag. This demonstrates the practical effect of the proposed inclusion policy; those flags are not the separate 20 examples used to calibrate CERA's intervals. The loader reads the dataset scores, but the independent reconstruction and sampling did not use them. This preflight did not execute a search or verify the proposed new evaluator.

The pinned IRED representation cache passed the existing verified loader for 8,586 entries, and its SHA-256 matched the configured pin. The example reward specification also matched the prior study's pinned SHA-256. At this check, the filesystem reported 194 GB available and the previous 90-run IRED directory occupied 565 MB; neither observation guarantees sufficient space for a new run or future availability. No Gemini request, quota check or billing check was made.

## Runbook

Varun selected an unrestricted eligible candidate pool and subsequently authorized implementation and the remaining project work. The [study plan](ired_low_change.md#plan) specifies the exploratory low-change start and its limitations. Use the existing pinned reward specification, IRED dataset and representation cache. The Gemini method may incur charges; configured credentials and model were present at preflight, but provider quota and actual billing were not checked.

Run ten seeds and nine methods in a new output directory:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend:. python3 -m scripts.multiprotein.run_matched_proteins output/multiprotein/ired_low_change/ired_low_change_61_70 --dataset ired --initial-pool train --seeds 61 62 63 64 65 66 67 68 69 70 --methods random greedy fixed repair gemini_repair ucb ei genetic adalead --specification configs/reward_spec_example.json --targeted-disagreement --direct-diversity
```

The command records a manifest before running and writes a separate status per method and seed. If interrupted, preserve the directory. `--resume` verifies the manifest and completed-record hashes; failed or interrupted statuses are preserved and are not automatically rerun. Investigate any failure and report it without erasing evidence. Do not feed results back into configuration.

After all 90 statuses are terminal, audit before reporting, then evaluate to a new file:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend:. python3 -m scripts.multiprotein.audit_matched_proteins output/multiprotein/ired_low_change/ired_low_change_61_70 --ired-low-change
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend:. python3 -m scripts.multiprotein.evaluate_matched_proteins output/multiprotein/ired_low_change/ired_low_change_61_70_report.json output/multiprotein/ired_low_change/ired_low_change_61_70 --specification configs/reward_spec_example.json --ired-low-change
```

The special audit and evaluator scopes require exactly IRED, seeds 61–70, all nine methods, both repair checks and the pinned specification. They check the starting pool's mutation limit and match the exact ordered sample; the existing full four-protein scope still requires its original eligible-start settings. The evaluator records mutation counts of selected variants. The independent audit reconstructs recorded decisions but does not refit every predictor or establish the scientific validity of the warnings.

## Findings

The [study plan](ired_low_change.md#plan) starts each method from the same 100 IRED variants with at most two substitutions and then permits selection from all eligible unmeasured variants with at most four substitutions. It is a retrospective search over previously measured variants, not the official static FLIP2 split evaluation or a laboratory experiment. IRED outcomes had already been inspected, so this is exploratory and not independent validation. All 90 runs, nine methods on each of ten seeds, reached completed runner status; early policy stops are retained below.

### Primary comparisons

At each method's actual stop, compared with fixed reward on the same starting seed, each repair policy produced a higher best score once, an equal score seven times and a lower score twice (absolute differences at most 1e-12 counted as equal). Both repair policies stopped after failed repairs in all ten runs. Each measured 410 new variants across its ten runs, versus 1,000 for fixed reward; their per-run median was 35 versus 100. Each accepted five repairs. For every seed the two repair policies had the same final best score and measurement count; this does not establish equivalence, identical choices or a causal effect of repair.

The starting observations already included a top-1% eligible variant in six of ten seeds. The eligible-pool optimum and top-1% threshold are retrospective evaluator-only references, not biological optima. The 1% result is a hit indicator, not the fraction of all top variants found.

| Method | Median best score | Median new measurements | Runs finding a top-1% variant | Selected variants with 3 or 4 substitutions |
| --- | ---: | ---: | ---: | ---: |
| Random | 1.941357 | 100 | 8/10 | 426/1,000 |
| Greedy prediction | 1.867707 | 100 | 9/10 | 676/1,000 |
| Fixed reward | 1.939862 | 100 | 10/10 | 318/1,000 |
| Rule-based repair | 1.799749 | 35 | 9/10 | 175/410 |
| Gemini-assisted repair | 1.799749 | 35 | 9/10 | 175/410 |
| Mean plus spread | 1.674131 | 100 | 8/10 | 695/1,000 |
| Expected improvement | 2.020899 | 100 | 9/10 | 817/1,000 |
| Finite-pool recombination | 1.782530 | 100 | 10/10 | 6/1,000 |
| AdaLead-style search | 1.674131 | 8.5 | 7/10 | 0/141 |

The genetic and AdaLead-style methods are finite-pool adaptations, and expected improvement uses ensemble spread as an approximation. AdaLead-style search stopped for lack of available neighbors in all ten runs; it never selected a variant with more than two substitutions. The remaining methods did not all spend the same number of measurements, so medians at actual stop are comparisons of complete policies under a shared maximum, not equal-spending comparisons. Ten starting samples reuse one protein's measured dataset and are not ten independent proteins.

### Ranges and provider calls

Across ten runs, fixed reward covered 897 of 1,000 newly measured scores with previously recorded prediction ranges. Each repair policy covered 364 of 410. These whole-run counts include observations before any accepted repair and observations in runs without one; they do not measure after-repair coverage or prove a coverage guarantee. Fixed reward had one observed recovery after a coverage warning, one warning with insufficient later measurements, and eight runs without a coverage warning. Neither repair policy recorded a coverage warning. Adaptive sampling and dependent runs limit interpretation of all coverage fractions.

The Gemini-assisted runs recorded 25 request attempts, 25 valid advice selections, zero recorded fallbacks and 3,630 reported total tokens. The existing client may discard usage metadata from rejected responses, so this number is not a verified billing total. Actual charges and quota were not checked. Provider prompts use sanitized warning/menu information rather than sequences and measured fitness values.

### Verification

The [audit output](../../../output/multiprotein/ired_low_change/ired_low_change_61_70_audit.json) is captured directly from the successful audit command. It reports 90 completed records, 703 selection batches, 135 repair replays, one representative distance round and two representative local-proposal rounds. It reconstructs recorded decisions but does not refit every predictor or validate warnings as scientific diagnoses. The audit script SHA-256 was `d15c3b7554735791b32cab5589cfa8404226d78141bcb58e762d2f5322bc343d`; the study manifest SHA-256 was `cffee9c128b4232cea6812a094ca82a992cf4501429ccff9a4c4220f6383b37e`.

The [evaluation report](../../../output/multiprotein/ired_low_change/ired_low_change_61_70_report.json) contains all per-seed curves, mutation counts, warning summaries, stops and 80 paired comparisons; its SHA-256 was `06fac77f92674e47006cbcbd5649e4f97fc5f5621281d705977890240eb5188e`. A separate one-off calculation verified compressed and uncompressed fingerprints, source scores, selected mutation counts, range counts, final best scores and all 80 paired differences against the 90 saved records. That check was not saved as a reusable audit. Full backend tests passed 107 tests before the study, and the previous four-protein report was reproduced byte for byte after the implementation change.
