<div align="center">

# Held-out shift prediction: exploratory protocol

Protocol and findings

</div>

## Protocol

The completed active-search studies did not test prediction on a held-out side of either benchmark split. This separate **static prediction** check uses the existing predictors and frozen settings; it is not an active-search comparison, a repair evaluation, or an official FLIP2 submission. Previous IRED and Hydro outcomes have already been viewed, so this is exploratory rather than an independent confirmation.

Use the four existing datasets and reference sequences. Limit both sides to variants with at most four substitutions, as in the search studies. On each protein and seed 121–130, sample 100 examples from the benchmark training side in its original file order; randomly reserve 20 for interval calibration using seed 2000 plus the starting seed, and fit the existing five-member predictor on the remaining 80 using the existing five-fold regularization selection and member-seed procedure. Predict every eligible benchmark test-side variant with a mean and an interval. Save all predictions and source fingerprints before calculating any test-side metrics. The predictor receives only selected training scores; it never receives test-side scores. Benchmark validation-flagged rows within the train side are eligible, consistent with earlier searches. No settings are tuned using these held-out results.

The IRED split moves from at most two substitutions in training to more in test. Hydro's low-to-high split uses measured fitness to define membership, so choosing the training group and test group uses privileged score-derived information. Its results describe this retrospective benchmark construction, not a way to select a real-world pool without already knowing scores. The mutation cap excludes part of each official test split. The official [FLIP2 definitions](https://flip.protein.properties/) describe these split types; this capped, 100-example adaptation is not directly comparable to full benchmark results.

After prediction artifacts are frozen, a separate evaluator verifies source identities, selected IDs, split membership, uniqueness, prediction completeness and finite values. For each seed and protein, report Spearman rank correlation, mean absolute prediction error, interval coverage and interval width, with denominators. Report per-start values and the median across starts without pooling different proteins. Mark rank correlation unavailable if a score or prediction vector is constant. Ranges use the existing held-back training scores, but distribution shift and dependent variant measurements invalidate an automatic claim of 90% coverage; the [conformal prediction literature](https://arxiv.org/abs/2107.07511) states the assumptions behind standard coverage guarantees. These ten starts are repeated samples from fixed data, not independent proteins or experiments.

Checks: synthetic fixtures must reject test-side score exposure, missing or duplicated predictions, altered identities and non-finite numbers; reconstruct sampled IDs and interval calculations independently. Run the full backend tests, freeze implementation before generating actual predictions, and retain the original dataset fingerprints. Do not claim this experiment evaluates reward repair or completes the sequential shift-search requirement.

## Findings

The existing predictor was fitted ten times per protein, each time from 100 training-side variants, and evaluated on eligible variants from the opposite side of a FLIP2 split. Predictions were [saved and committed](../../../output/heldout_shift_predictions_121_130.json) before test-side results were calculated. This is a static prediction check, not a search, a reward-repair comparison, or an official FLIP2 score. The [protocol](heldout_shift_prediction.md#protocol) was written after earlier test outcomes had been inspected; these results are exploratory.

| Protein and split | Held-out variants per run | Median rank correlation | Median interval coverage | Coverage range across ten starts |
| --- | ---: | ---: | ---: | ---: |
| IRED, mutation count | 3,225 | 0.097 | 90.0% | 69.0%–99.0% |
| Hydro P06241, lower to higher fitness | 747 | 0.051 | 0.0% | 0.0%–0.3% |
| Hydro P01053, lower to higher fitness | 579 | 0.189 | 11.7% | 0.2%–30.1% |
| Hydro P0A9X9, lower to higher fitness | 2,215 | 0.270 | 10.6% | 3.8%–28.6% |

Rank correlation describes how similarly predicted and measured scores order the held-out variants: 1 is identical ranking, 0 indicates no monotonic association, and -1 is reversed ranking. Coverage is the fraction of measured scores falling inside the predictor's intervals. The table reports the median of ten starting samples, not a combined measurement count. Individual outcomes and mean absolute errors appear in the [evaluation](../../../output/heldout_shift_evaluation_121_130.json).

The Hydro intervals, calibrated on lower-fitness training examples, covered few higher-fitness held-out values in this experiment. The result does not establish that a repair could correct the failure. Hydro split membership was constructed from measured fitness, so the training/test distinction uses privileged outcome information that a real search would not normally have. The four-substitution cap excludes some official test variants. IRED's median coverage is near 90%, but varied substantially across starts; neither that median nor any of these adaptive dataset splits establishes a formal prediction-interval guarantee. All ten runs share the same measured proteins and are not independent biological replications.

The [audit](../../../output/heldout_shift_audit_121_130.json) refitted all 200 individual models, reconstructed calibration intervals and checked 67,660 predictions. It independently recalculated rank correlation, errors, coverage and medians, and rejected a deliberately altered result. Refitting used the same underlying predictor implementation, so it does not independently establish the correctness of that algorithm or biological labels. The evaluator does not tune parameters from held-out scores. Reproduce the audit with `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend:. python3 -m scripts.heldout.audit_heldout_shifts output/heldout_shift_predictions_121_130.json output/heldout_shift_evaluation_121_130.json`.
