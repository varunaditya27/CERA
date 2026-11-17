# Additional retrospective search metrics

The [post-result protocol](additional_metrics_protocol.md) was applied to the completed four-protein comparison and the separate IRED low-change-start comparison. These are descriptive analyses of records whose outcomes had already been inspected, not prespecified significance tests or independent biological replications.

The top group includes every eligible variant whose score is at or above the score at rank `ceil(1% × pool size)`; ties at the boundary are included. Recall is the fraction of that group found, including the initial 100 observations. This differs from the previously reported yes/no result for finding at least one top variant.

| Study / protein | Eligible variants in top group | Fixed reward median recall | Rule-based repair median recall | Gemini-assisted repair median recall |
| --- | ---: | ---: | ---: | ---: |
| Four-protein IRED | 77 | 3.9% | 2.6% | 2.6% |
| Four-protein Hydro P06241 | 11 | 72.7% | 40.9% | 40.9% |
| Four-protein Hydro P01053 | 13 | 92.3% | 69.2% | 69.2% |
| Four-protein Hydro P0A9X9 | 30 | 25.0% | 20.0% | 20.0% |
| IRED low-change start | 77 | 1.3% | 1.3% | 1.3% |

Each median summarizes ten matched starts on the same measured protein, and the policies often used different numbers of new measurements. Initial observations contribute to the recall totals; the machine-readable results report initial and newly discovered top variants separately. Pool sizes, score distributions and starting-pool rules differ, so these percentages should not be interpreted as a direct comparison of biological difficulty across proteins or studies.

The reports also give cumulative regret over *new* measurements and its per-measurement mean, plus the mean pairwise sequence differences and, for predictor methods, the prediction-versus-measurement rank correlation for each selected batch. Cumulative totals are not directly comparable when a policy stops early: making fewer measurements can yield a smaller sum. Random selection and constant or too-small batches have an unavailable rank correlation, represented as null. These are descriptions of selected variants, not estimates for unselected variants or a causal effect of repair.

The later [after-repair coverage analysis](after_repair_coverage_findings.md) adds an explicitly defined first 30-measurement window following an accepted repair. Its output files supersede the files below for shared metric fields; the earlier outputs are retained for reproducibility.

- [Four-protein metrics](../output/matched_eval_51_60_additional_metrics.json): SHA-256 `058e9da17d2334085927371b714bdac5d2a569b23adf7bf424e0423a0e29ff9d`.
- [IRED low-change metrics](../output/ired_low_change_61_70_additional_metrics.json): SHA-256 `adfe9a01414cb332ba923e7f8d95adfa97d9c0114105f12667ddd95e2389fa38`.

The evaluator requires terminal statuses, study scope and matching source and record fingerprints, and reuses the existing validated run summaries. A separate one-off calculation read the saved records and source datasets and independently checked top-group counts and recall, cumulative regret, and all selected-batch correlations and sequence differences for 450 runs and 3,646 batches. It calculated ranks separately rather than calling the evaluator's correlation function. This check was not saved as a reusable audit. The backend suite passed 118 tests before the calculation; no new searches or provider calls were made.
