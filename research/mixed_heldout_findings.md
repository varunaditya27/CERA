# Mixed predictor: exploratory held-out protein comparison

Following the [recorded protocol](mixed_heldout_protocol.md), the mixed predictor generated predictions for ten matched starting samples on each of four protein groups. Predictions were saved in commit `3bb54e3` before this evaluation. Each group below reports the median across ten starts. Rank correlation describes how similarly the predicted and measured values order variants; mean absolute error is the average magnitude of the prediction error, in that dataset's score units; coverage is the fraction inside the prediction range.

| Protein | Median rank correlation, mixed / ridge | Median coverage, mixed / ridge | Median absolute error, mixed / ridge |
| --- | ---: | ---: | ---: |
| IRED | 0.074 / 0.097 | 89.8% / 90.0% | 0.968 / 0.961 |
| Hydro P06241 | 0.050 / 0.051 | 0.0% / 0.0% | 1.798 / 1.805 |
| Hydro P01053 | 0.238 / 0.189 | 8.0% / 11.7% | 1.187 / 1.181 |
| Hydro P0A9X9 | 0.271 / 0.270 | 8.9% / 10.6% | 0.649 / 0.636 |

These are separate medians, not medians of paired differences. The [paired comparison](../output/mixed_heldout_comparison_121_130.json) records each matched difference and its median; for example, the median paired rank-correlation difference for P01053 was +0.0337. The mixed predictor did not consistently improve these measures, and both predictors' ranges covered few higher-fitness Hydro examples. Score scales differ, so absolute errors must not be compared across proteins. These are descriptive observations, not evidence of general superiority or equivalence.

Both methods used the same initial and reserved examples, member seeds, held-out identifiers, four-substitution cap and score-free representations. A separate calculation recomputed all 40 mixed-run rank correlations, errors and coverage counts from the saved predictions and source measurements. The comparison script verifies matching assignments and evaluation-to-prediction hashes; it does not independently refit the predictors. Unit checks reject changed assignments and overlapping training/test identifiers. All results reuse previously examined data: Hydro split membership is fitness-derived, IRED train-side sampling includes validation-marked rows, and this is a static evaluation rather than a search, repair test, official benchmark score, or independent biological validation.

Artifacts: [predictions](../output/mixed_heldout_predictions_121_130.json), [evaluation](../output/mixed_heldout_evaluation_121_130.json), and [paired comparison](../output/mixed_heldout_comparison_121_130.json). Re-run the commands from the repository root with new output paths:

```sh
TORCH_DISABLE_NATIVE_JIT=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend python3 scripts/predict_mixed_heldout.py output/my-mixed-predictions.json
TORCH_DISABLE_NATIVE_JIT=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend python3 scripts/evaluate_mixed_heldout.py output/my-mixed-predictions.json output/my-mixed-evaluation.json
PYTHONPATH=backend python3 scripts/compare_mixed_heldout.py output/my-mixed-predictions.json output/heldout_shift_predictions_121_130.json output/my-mixed-evaluation.json output/heldout_shift_evaluation_121_130.json output/my-mixed-comparison.json
```
