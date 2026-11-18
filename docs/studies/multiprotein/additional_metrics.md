<div align="center">

# Additional retrospective study metrics

Protocol and findings

</div>

## Protocol

This post-result analysis fills reporting gaps in the synopsis using saved, already completed four-protein and IRED low-change records. It is exploratory: results were seen before these exact reporting choices were documented. It does not tune the search or establish causal effects. Evaluate only after all configured runs have terminal statuses and the relevant study scope, source fingerprints and record hashes have been checked.

For each eligible protein pool, sort scores descending and use the score at rank `ceil(0.01 × pool size)` as the cutoff. Every variant tied at or above that cutoff is included, so the positive set can exceed 1% of the pool. Report its actual size. Top-1% recall is the number of distinct qualifying variants found divided by that actual size. Report the count found in the initial 100, the additional count found in new measurements and their combined recall; do not call a yes/no top-1% hit recall. The full score pool is used only by the evaluator, after selection has ended.

For each new measurement, regret is the best score in the eligible pool minus that measurement's score. Sum those differences for cumulative regret, excluding the initial 100, and report both the sum and its measurement count. This sum is not comparable without qualification across policies that stop at different times: fewer measurements can produce a smaller sum. Also report its per-measurement mean when at least one new measurement exists. This finite-pool reference is the best observed score in the available dataset, not a biological optimum. [Sen et al.](https://proceedings.mlr.press/v89/sen19a/sen19a.pdf) distinguish final simple regret from accumulated query regret.

For every measured batch, report the average pairwise number of different sequence positions and, where recorded prediction means and nonconstant measurements exist, the Spearman rank correlation between predictions made before reveal and subsequently measured scores. A batch with fewer than two distinct selected sequences has no pairwise average. Rank correlation is unavailable for random selection, constant inputs or fewer than two observations; record it as null, not zero. Scores, correlations and sequence diversity concern the selected batch and cannot be assumed to describe unselected variants. [SciPy's documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.spearmanr.html) describes constant-input behavior.

For an accepted repair, separately report coverage of the first 30 measurements selected *after the first accepted repair* in that run, using each measurement's own pre-reveal range. Use the previously approved 26–28 of 30 band around the 90% target. Classify runs as no accepted repair, insufficient later measurements, or a fully observed first window; do not substitute an incomplete window or silently exclude it. The first accepted repair may be followed by other repairs, and the same selected measurements are affected by adaptive search. This descriptive window does not prove a causal effect, and it is not the existing recovery-after-first-warning metric. The study's previously inspected outcomes make this a post-result analysis, not an independent test of the synopsis target on its originally proposed shift splits.

Preserve every seed, method, status, actual count and batch. Verify source and record fingerprints, matched starts, measurement chronology and source scores using the existing evaluator before calculating the additional metrics. Test ties at the top cutoff, initial versus newly found variants, a short batch, undefined correlations and invalid records. Report per protein and method without pooling raw scores across proteins; no independent-protein confidence interval or new significance test is implied.

## Findings

The [post-result protocol](additional_metrics.md#protocol) was applied to the completed four-protein comparison and the separate IRED low-change-start comparison. These are descriptive analyses of records whose outcomes had already been inspected, not prespecified significance tests or independent biological replications.

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

The later [after-repair coverage analysis](../repair/after_repair_coverage.md) adds an explicitly defined first 30-measurement window following an accepted repair. Its output files supersede the files below for shared metric fields; the earlier outputs are retained for reproducibility.

- [Four-protein metrics](../../../output/matched_eval_51_60_additional_metrics.json): SHA-256 `058e9da17d2334085927371b714bdac5d2a569b23adf7bf424e0423a0e29ff9d`.
- [IRED low-change metrics](../../../output/ired_low_change_61_70_additional_metrics.json): SHA-256 `adfe9a01414cb332ba923e7f8d95adfa97d9c0114105f12667ddd95e2389fa38`.

The evaluator requires terminal statuses, study scope and matching source and record fingerprints, and reuses the existing validated run summaries. A separate one-off calculation read the saved records and source datasets and independently checked top-group counts and recall, cumulative regret, and all selected-batch correlations and sequence differences for 450 runs and 3,646 batches. It calculated ranks separately rather than calling the evaluator's correlation function. This check was not saved as a reusable audit. The backend suite passed 118 tests before the calculation; no new searches or provider calls were made.
