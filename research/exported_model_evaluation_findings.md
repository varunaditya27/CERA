# Exploratory comparison of the exported Amylase model

The saved mixed model and a five-ridge group were compared under the [recorded protocol](exported_model_evaluation_protocol.md), using the same 100 fitting and 20 range-setting examples. The remaining eligible pool contained 3,155 measured variants. The [machine-readable result](../output/amylase_hybrid_seed181_evaluation.json) records source fingerprints, the evaluation-set fingerprint and exact metrics.

| Measure | Mixed model | Five-ridge group |
| --- | ---: | ---: |
| Average absolute prediction error | 0.04995 | 0.05085 |
| Root mean squared prediction error | 0.05596 | 0.05631 |
| Measured scores inside range | 3,018 / 3,155 (95.66%) | 3,032 / 3,155 (96.10%) |
| Full range width | 0.19297 | 0.19393 |

The mixed group had slightly lower errors in this one comparison; the ridge group covered slightly more observed scores with a slightly wider range. These numbers do not show that either method is generally better. The model's 120 examples came from a prior adaptive search, and this development dataset has already informed project work. The unobserved pool is not an independent biological replication, a prospective search comparison, or an evaluation on other proteins. The 20 reserved measurements were used to set the range and were excluded from this evaluation. There is no guarantee that these coverage values apply to future selections.

To reproduce the result, choose a new output path:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend python3 scripts/evaluate_exported_hybrid.py output/amylase_hybrid_seed181_final.npz output/my-model-evaluation.json --expected-sha256 747968886935e3890fa0d4d9c95d1962a024cf35a4c55ac19672cd1e6a17e737
```

The evaluator refuses to overwrite a result. This comparison is not an independent validation of the model exporter or the training implementation; the separate [model audit](hybrid_model_export_findings.md) addresses reproducibility of the fitted artifact.
