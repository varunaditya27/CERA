# Reusable Amylase development model

The [model archive](../output/amylase_hybrid_seed181_final.npz) contains a post-episode refit of three ridge predictors and two neural networks. Its SHA-256 fingerprint is `747968886935e3890fa0d4d9c95d1962a024cf35a4c55ac19672cd1e6a17e737`. It is a development artifact, not a validated laboratory model. The earlier [GPU episode](hybrid_predictor_findings.md) did not evaluate this refit, which includes its final revealed batch.

The refit used 120 observed measurements: 100 were available for fitting and 20 were reserved to set the prediction range. Within the 100, each neural network used 80 training examples and 20 early-stopping examples; the ridge models used all 100. The range radius was 0.09648729572889815. This radius is not a guarantee of future coverage.

The [separate audit](../output/amylase_hybrid_seed181_final_audit.json) checked the parent record and reconstructed the fit on the same GPU and software environment. CPU predictions from the loaded archive matched that refit on all 3,706 cached representations, with maximum differences of 3.98e-9 for the mean and 7.70e-9 for the spread. This is a reproducibility check, not an independent implementation of training or a test of biological accuracy. A fresh CPU process also loaded and ran the archive without importing PyTorch. The archive contains numeric weights and metadata and is loaded without Python object deserialization; see [NumPy's documentation](https://numpy.org/doc/stable/reference/generated/numpy.load.html). The external fingerprint must come from a trusted source.

To use the saved model with the checked local representation cache, run from the repository root with `PYTHONPATH=backend`:

```python
from app.experiments.hybrid_snapshot import load_hybrid_snapshot
from app.features.amylase_representations import load_verified_representations

model = load_hybrid_snapshot(
    'output/amylase_hybrid_seed181_final.npz',
    expected_sha256='747968886935e3890fa0d4d9c95d1962a024cf35a4c55ac19672cd1e6a17e737',
)
vectors = load_verified_representations()
identifier = next(iter(vectors))
prediction = model.predict([vectors[identifier]])
print(identifier, prediction['mean'][0], prediction['lower'][0], prediction['upper'][0])
```

The representation is a 320-number description of a protein sequence produced by the specific frozen ESM-2 model and settings in the cache. The archive does not contain ESM-2 and cannot verify that an arbitrary supplied vector uses the right representation. The archive also does not contain raw sequences or measured scores. See the [export protocol](hybrid_model_export_protocol.md) for fitting roles and provenance. The audit refit requires the matching source files, cache, software, and device; loading the archive for inference needs NumPy and the matching representation, not a GPU.

A subsequent [exploratory comparison](exported_model_evaluation_findings.md) measured this model and a matched five-ridge group on the remaining eligible Amylase variants. The mixed group has not been prospectively compared in a search, evaluated on test proteins, or validated with new laboratory measurements. Do not interpret this artifact as evidence that a larger representation model would improve the result.
