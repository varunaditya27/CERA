# IRED low-change start: exploratory findings

The [study plan](ired_low_change_study_plan.md) starts each method from the same 100 IRED variants with at most two substitutions and then permits selection from all eligible unmeasured variants with at most four substitutions. It is a retrospective search over previously measured variants, not the official static FLIP2 split evaluation or a laboratory experiment. IRED outcomes had already been inspected, so this is exploratory and not independent validation. All 90 runs, nine methods on each of ten seeds, reached completed runner status; early policy stops are retained below.

## Primary comparisons

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

## Ranges and provider calls

Across ten runs, fixed reward covered 897 of 1,000 newly measured scores with previously recorded prediction ranges. Each repair policy covered 364 of 410. These whole-run counts include observations before any accepted repair and observations in runs without one; they do not measure after-repair coverage or prove a coverage guarantee. Fixed reward had one observed recovery after a coverage warning, one warning with insufficient later measurements, and eight runs without a coverage warning. Neither repair policy recorded a coverage warning. Adaptive sampling and dependent runs limit interpretation of all coverage fractions.

The Gemini-assisted runs recorded 25 request attempts, 25 valid advice selections, zero recorded fallbacks and 3,630 reported total tokens. The existing client may discard usage metadata from rejected responses, so this number is not a verified billing total. Actual charges and quota were not checked. Provider prompts use sanitized warning/menu information rather than sequences and measured fitness values.

## Verification

The [audit output](../output/ired_low_change_61_70_audit.json) is captured directly from the successful audit command. It reports 90 completed records, 703 selection batches, 135 repair replays, one representative distance round and two representative local-proposal rounds. It reconstructs recorded decisions but does not refit every predictor or validate warnings as scientific diagnoses. The audit script SHA-256 was `d15c3b7554735791b32cab5589cfa8404226d78141bcb58e762d2f5322bc343d`; the study manifest SHA-256 was `cffee9c128b4232cea6812a094ca82a992cf4501429ccff9a4c4220f6383b37e`.

The [evaluation report](../output/ired_low_change_61_70_report.json) contains all per-seed curves, mutation counts, warning summaries, stops and 80 paired comparisons; its SHA-256 was `06fac77f92674e47006cbcbd5649e4f97fc5f5621281d705977890240eb5188e`. A separate one-off calculation verified compressed and uncompressed fingerprints, source scores, selected mutation counts, range counts, final best scores and all 80 paired differences against the 90 saved records. That check was not saved as a reusable audit. Full backend tests passed 107 tests before the study, and the previous four-protein report was reproduced byte for byte after the implementation change.
