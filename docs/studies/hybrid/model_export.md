<div align="center">

# Exporting a reusable mixed predictor

Protocol and findings

</div>

## Protocol

The GPU pilot currently discards its fitted models when the process exits. To make the predictor reusable, provide a separate export step for a completed mixed-predictor Amylase record. This is a research artifact, not a validated model for laboratory decisions.

Verify the saved episode's source, candidate decisions, fitting roles, final stop and source measurements before export. Reconstruct the known observations exclusively from the initial and reveal events. Refit the three ridge and two neural members on those observations after the episode, preserving the episode's 20 range-setting examples and excluding them from fitting. Choose the next member seeds from the recorded deterministic member-seed sequence; record them, the full fitting and internal neural-validation roles, model settings, source fingerprints and the parent record's hash. Recalculate the nominal 90% range radius from the reserved observations. This final refit may use the scores from the last revealed batch, unlike the last predictor saved in the episode. Its predictions and coverage are not evaluated by the previous episode; the existing test results do not measure this refitted model's performance.

Save numeric model weights, normalization values, radius and JSON metadata in a new compressed NumPy archive. Do not serialize executable Python objects. Load with `allow_pickle=False`, validate names, shapes, numeric types, finite values and metadata, and never overwrite an existing artifact. [NumPy's loading documentation](https://numpy.org/doc/stable/reference/generated/numpy.load.html) explains why loading pickled objects can execute code. Write the completed artifact atomically and check that a fresh load reproduces in-memory predictions within a stated numerical tolerance. Supply an inference API for a caller-provided matrix of verified ESM representations. The artifact does not contain ESM itself, raw sequences, source scores, credentials or a guarantee that supplied vectors came from the right representation model.

Tests must cover model output parity after a save/load round trip, unsupported or tampered arrays, invalid shapes/nonfinite inputs, refusal to overwrite an existing file, and fitting/calibration role separation. Execute one final export from the already audited corrected GPU episode, independently reload it on CPU and compare its predictions with the in-memory GPU model before reporting. Record software, device and fingerprints. Do not describe that check as biological validation or as evidence that the model outperforms the baseline.

## Findings

The [model archive](../../../output/amylase_hybrid_seed181_final.npz) contains a post-episode refit of three ridge predictors and two neural networks. Its SHA-256 fingerprint is `747968886935e3890fa0d4d9c95d1962a024cf35a4c55ac19672cd1e6a17e737`. It is a development artifact, not a validated laboratory model. The earlier [GPU episode](hybrid_predictor.md#findings) did not evaluate this refit, which includes its final revealed batch.

The refit used 120 observed measurements: 100 were available for fitting and 20 were reserved to set the prediction range. Within the 100, each neural network used 80 training examples and 20 early-stopping examples; the ridge models used all 100. The range radius was 0.09648729572889815. This radius is not a guarantee of future coverage.

The [separate audit](../../../output/amylase_hybrid_seed181_final_audit.json) checked the parent record and reconstructed the fit on the same GPU and software environment. CPU predictions from the loaded archive matched that refit on all 3,706 cached representations, with maximum differences of 3.98e-9 for the mean and 7.70e-9 for the spread. This is a reproducibility check, not an independent implementation of training or a test of biological accuracy. A fresh CPU process also loaded and ran the archive without importing PyTorch. The archive contains numeric weights and metadata and is loaded without Python object deserialization; see [NumPy's documentation](https://numpy.org/doc/stable/reference/generated/numpy.load.html). The external fingerprint must come from a trusted source.

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

The representation is a 320-number description of a protein sequence produced by the specific frozen ESM-2 model and settings in the cache. The archive does not contain ESM-2 and cannot verify that an arbitrary supplied vector uses the right representation. The archive also does not contain raw sequences or measured scores. See the [export protocol](model_export.md#protocol) for fitting roles and provenance. The audit refit requires the matching source files, cache, software, and device; loading the archive for inference needs NumPy and the matching representation, not a GPU.

A subsequent [exploratory comparison](exported_model_evaluation.md#findings) measured this model and a matched five-ridge group on the remaining eligible Amylase variants. The mixed group has not been prospectively compared in a search, evaluated on test proteins, or validated with new laboratory measurements. Do not interpret this artifact as evidence that a larger representation model would improve the result.
