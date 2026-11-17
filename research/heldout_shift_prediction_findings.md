# Exploratory held-out shift prediction findings

The existing predictor was fitted ten times per protein, each time from 100 training-side variants, and evaluated on eligible variants from the opposite side of a FLIP2 split. Predictions were [saved and committed](../output/heldout_shift_predictions_121_130.json) before test-side results were calculated. This is a static prediction check, not a search, a reward-repair comparison, or an official FLIP2 score. The [protocol](heldout_shift_prediction_protocol.md) was written after earlier test outcomes had been inspected; these results are exploratory.

| Protein and split | Held-out variants per run | Median rank correlation | Median interval coverage | Coverage range across ten starts |
| --- | ---: | ---: | ---: | ---: |
| IRED, mutation count | 3,225 | 0.097 | 90.0% | 69.0%–99.0% |
| Hydro P06241, lower to higher fitness | 747 | 0.051 | 0.0% | 0.0%–0.3% |
| Hydro P01053, lower to higher fitness | 579 | 0.189 | 11.7% | 0.2%–30.1% |
| Hydro P0A9X9, lower to higher fitness | 2,215 | 0.270 | 10.6% | 3.8%–28.6% |

Rank correlation describes how similarly predicted and measured scores order the held-out variants: 1 is identical ranking, 0 indicates no monotonic association, and -1 is reversed ranking. Coverage is the fraction of measured scores falling inside the predictor's intervals. The table reports the median of ten starting samples, not a combined measurement count. Individual outcomes and mean absolute errors appear in the [evaluation](../output/heldout_shift_evaluation_121_130.json).

The Hydro intervals, calibrated on lower-fitness training examples, covered few higher-fitness held-out values in this experiment. The result does not establish that a repair could correct the failure. Hydro split membership was constructed from measured fitness, so the training/test distinction uses privileged outcome information that a real search would not normally have. The four-substitution cap excludes some official test variants. IRED's median coverage is near 90%, but varied substantially across starts; neither that median nor any of these adaptive dataset splits establishes a formal prediction-interval guarantee. All ten runs share the same measured proteins and are not independent biological replications.

The [audit](../output/heldout_shift_audit_121_130.json) refitted all 200 individual models, reconstructed calibration intervals and checked 67,660 predictions. It independently recalculated rank correlation, errors, coverage and medians, and rejected a deliberately altered result. Refitting used the same underlying predictor implementation, so it does not independently establish the correctness of that algorithm or biological labels. The evaluator does not tune parameters from held-out scores. Reproduce the audit with `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend python3 scripts/audit_heldout_shifts.py output/heldout_shift_predictions_121_130.json output/heldout_shift_evaluation_121_130.json`.
