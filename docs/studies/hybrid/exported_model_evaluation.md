<div align="center">

# Post-episode Amylase model check

Protocol and findings

</div>

## Protocol

Recorded before executing the check. Compare the exported seed-181 mixed model against a newly fitted five-ridge group using the same 100 fitting identifiers, 20 range-setting identifiers, cross-validation seed and member-seed list. The three ridge members within the mixed group use the same fitting procedure; the two additional ridge members replace the neural members in the comparison. Set each group's interval radius independently using its predictions on the same 20 reserved examples.

Evaluate both groups on every eligible Amylase variant with at most four substitutions that was not among the 120 observed examples. Report mean absolute error, root mean squared error, the number and fraction of measured scores inside the prediction range, and range width. The eligible set is a fixed retrospective pool, not an independent biological replicate or the official held-out split. Starting examples and subsequent selections were determined by the earlier adaptive episode; the rest of this development dataset has been examined in prior project work. This is therefore an exploratory conditional comparison for one observed history, not a fair prospective comparison of search policies, evidence of generalization to other proteins, or justification for model tuning. Test protein outcomes must not be used to change this protocol.

The evaluator verifies the source, reference, representation-cache and exported-model fingerprints; only the 120 observed scores are supplied to the ridge fitting and range-setting routines. It excludes all 120 from evaluation and will not overwrite an existing result. The earlier audit separately checked the saved mixed model's fit against its parent episode. Mean absolute error is the average absolute difference between predicted and measured scores ([definition](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.mean_absolute_error.html)); lower is better. Coverage is descriptive and is not a guarantee under adaptive selection. Source separation is needed to avoid leaking evaluation scores into fitting ([guidance](https://scikit-learn.org/stable/common_pitfalls.html)).

## Findings

The saved mixed model and a five-ridge group were compared under the [recorded protocol](exported_model_evaluation.md#protocol), using the same 100 fitting and 20 range-setting examples. The remaining eligible pool contained 3,155 measured variants. The [machine-readable result](../../../output/amylase_hybrid_seed181_evaluation.json) records source fingerprints, the evaluation-set fingerprint and exact metrics.

| Measure | Mixed model | Five-ridge group |
| --- | ---: | ---: |
| Average absolute prediction error | 0.04995 | 0.05085 |
| Root mean squared prediction error | 0.05596 | 0.05631 |
| Measured scores inside range | 3,018 / 3,155 (95.66%) | 3,032 / 3,155 (96.10%) |
| Full range width | 0.19297 | 0.19393 |

The mixed group had slightly lower errors in this one comparison; the ridge group covered slightly more observed scores with a slightly wider range. These numbers do not show that either method is generally better. The model's 120 examples came from a prior adaptive search, and this development dataset has already informed project work. The unobserved pool is not an independent biological replication, a prospective search comparison, or an evaluation on other proteins. The 20 reserved measurements were used to set the range and were excluded from this evaluation. There is no guarantee that these coverage values apply to future selections.

To reproduce the result, choose a new output path:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend:. python3 -m scripts.hybrid.evaluate_exported_hybrid output/amylase_hybrid_seed181_final.npz output/my-model-evaluation.json --expected-sha256 747968886935e3890fa0d4d9c95d1962a024cf35a4c55ac19672cd1e6a17e737
```

The evaluator refuses to overwrite a result. This comparison is not an independent validation of the model exporter or the training implementation; the separate [model audit](model_export.md#findings) addresses reproducibility of the fitted artifact.
