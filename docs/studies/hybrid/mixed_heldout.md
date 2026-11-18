<div align="center">

# Mixed predictor on held-out protein variants

Protocol and findings

</div>

## Protocol

Recorded before running this comparison on 18 November 2026. Reuse the existing capped static shift study's four proteins, ten starts (121–130), starting samples, score-independent assignment of 20 range-setting examples, and five member seeds. Compare the existing five-ridge predictions with the existing three-ridge/two-neural predictor trained on the same 80 fitting examples; the latter retains its existing internal early-stopping split. Use the checked representation caches and CUDA. Save predictions and configuration before calculating any test-side metrics. Report each protein separately, including rank correlation, mean absolute error and prediction-range coverage, with per-start paired differences. Do not select or tune a model using these outcomes.

This is retrospective and exploratory: earlier results on these proteins have already been examined, Hydro split membership is based on measured fitness, IRED train membership includes validation-marked rows, and the four-substitution cap omits some benchmark variants. It is not an official FLIP2 benchmark, active search, independent biological replication, or a test of reward repair. The same frozen data are used to fit each method, not to select hyperparameters from held-out outcomes; see [scikit-learn's leakage guidance](https://scikit-learn.org/stable/common_pitfalls.html#data-leakage). Differences across hardware and software can occur even with matching inputs; see [PyTorch numerical accuracy](https://docs.pytorch.org/docs/stable/notes/numerical_accuracy.html).

## Findings

Following the [recorded protocol](mixed_heldout.md#protocol), the mixed predictor generated predictions for ten matched starting samples on each of four protein groups. Predictions were saved in commit `3bb54e3` before this evaluation. Each group below reports the median across ten starts. Rank correlation describes how similarly the predicted and measured values order variants; mean absolute error is the average magnitude of the prediction error, in that dataset's score units; coverage is the fraction inside the prediction range.

| Protein | Median rank correlation, mixed / ridge | Median coverage, mixed / ridge | Median absolute error, mixed / ridge |
| --- | ---: | ---: | ---: |
| IRED | 0.074 / 0.097 | 89.8% / 90.0% | 0.968 / 0.961 |
| Hydro P06241 | 0.050 / 0.051 | 0.0% / 0.0% | 1.798 / 1.805 |
| Hydro P01053 | 0.238 / 0.189 | 8.0% / 11.7% | 1.187 / 1.181 |
| Hydro P0A9X9 | 0.271 / 0.270 | 8.9% / 10.6% | 0.649 / 0.636 |

These are separate medians, not medians of paired differences. The [paired comparison](../../../output/mixed_heldout_comparison_121_130.json) records each matched difference and its median; for example, the median paired rank-correlation difference for P01053 was +0.0337. The mixed predictor did not consistently improve these measures, and both predictors' ranges covered few higher-fitness Hydro examples. Score scales differ, so absolute errors must not be compared across proteins. These are descriptive observations, not evidence of general superiority or equivalence.

Both methods used the same initial and reserved examples, member seeds, held-out identifiers, four-substitution cap and score-free representations. The [refit audit](../../../output/mixed_heldout_audit_121_130.json) rebuilt all 40 mixed groups (200 individual models) on the same GPU, checked the disjoint training and range-setting roles, reproduced 67,660 predictions within an absolute tolerance of 1e-5 and recalculated each reported metric and median. It uses the same fitting implementation; reproduction on this machine does not establish scientific validity or identical behavior on other systems. The comparison script verifies matching assignments and evaluation-to-prediction hashes. Unit checks reject changed assignments, overlapping training/test identifiers and an evaluation tied to different predictions. All results reuse previously examined data: Hydro split membership is fitness-derived, IRED train-side sampling includes validation-marked rows, and this is a static evaluation rather than a search, repair test, official benchmark score, or independent biological validation.

Artifacts: [predictions](../../../output/mixed_heldout_predictions_121_130.json), [evaluation](../../../output/mixed_heldout_evaluation_121_130.json), and [paired comparison](../../../output/mixed_heldout_comparison_121_130.json). Re-run the commands from the repository root with new output paths:

```sh
TORCH_DISABLE_NATIVE_JIT=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend:. python3 -m scripts.hybrid.predict_mixed_heldout output/my-mixed-predictions.json
TORCH_DISABLE_NATIVE_JIT=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend:. python3 -m scripts.hybrid.evaluate_mixed_heldout output/my-mixed-predictions.json output/my-mixed-evaluation.json
PYTHONPATH=backend:. python3 -m scripts.hybrid.compare_mixed_heldout output/my-mixed-predictions.json output/heldout_shift_predictions_121_130.json output/my-mixed-evaluation.json output/heldout_shift_evaluation_121_130.json output/my-mixed-comparison.json
TORCH_DISABLE_NATIVE_JIT=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend:. python3 -m scripts.hybrid.audit_mixed_heldout output/my-mixed-predictions.json output/my-mixed-evaluation.json output/my-mixed-audit.json
```
