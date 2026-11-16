# Amylase prediction-range pilot

Completed 16 November 2026 under the [development plan](prediction_ranges_development_plan.md). This single exploratory run checks the workflow, not a general coverage guarantee, a CERA repair, or a final evaluation.

## Setup

Used the pinned 3,706-sequence ESM-2 representation cache and the existing amylase runner. The initial-set seed was 1, the role-assignment seed 3, and the member-seed generator seed 4. Of 100 initial measurements, 80 were available for fitting and model selection; 20 were reserved for range setting. Each of five ridge predictors was fitted on its own reproducibly resampled fitting set after cross-validation selected a penalty on the unique fitting examples. After every batch, newly revealed measurements became available for the next fitting step. Scores of the 20 reserved examples were not passed directly to fitting or model selection.

For each round, the mean of the five predictions determined selection. The population standard deviation across members was recorded as a disagreement signal; it was not used as the range width. A symmetric range was set by the 19th smallest absolute error on the 20 reserved examples. The target was nominally 90%, but adaptive selection and reuse of range-setting data prevent assuming the standard guarantee. No uncertainty penalty, warning detector or repair was used.

Run command:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend python3 scripts/run_prediction_pilot.py output/amylase_range_pilot_seed1 --seed 1
```

The script reported 10 batches in 1.6667 seconds; that duration includes run creation, fitting, prediction, logging and report generation, but excludes loading and validating the cache. It is one local timing, not a benchmark. Settings, fitting identifiers, member seeds, source hashes, pre-reveal predictions, intervals and revealed scores are in [run.jsonl](../output/amylase_range_pilot_seed1/run.jsonl).

## Observations

All **100 of 100** selected scores fell inside their previously recorded ranges. Mean range width across those scores was approximately **0.20337** in the dataset's score units; per-batch results are in [coverage.csv](../output/amylase_range_pilot_seed1/coverage.csv). Broad ranges can cover many scores while providing limited precision. Ten scores per batch make each batch coverage value change in increments of ten percentage points. The observed 100% is not evidence that future coverage is guaranteed, nor that 100% is intrinsically better than a better-calibrated narrower range.

The pilot selected 66 original-train and 34 original-test variants, counted by joining original split labels after the run; these labels were not supplied to the selector. The best observed score after 100 new measurements was 0.1569333333333333. This pilot changed both representation and predictor structure relative to the earlier one-hot greedy experiment, so its movement across the split cannot be attributed to either change separately.

## Verification and limitations

- Fifteen unit tests passed, including reserved-score isolation, unique data before cross-validation, reproducible resampling, finite-sample rank and ties, invalid ranges, pre-reveal ordering, report reconstruction and cache fingerprint rejection.
- Independently audited each batch's candidate ranking, recorded fitting/reserved separation, member seed count, radius and bounds, unique queries, source scores, budget and reconstructed coverage table. All ten batches passed.
- Independently reconstructed the first round using the recorded fitting data and member seeds: the penalty was 0.1; the range-setting radius was 0.09607034487804328; selected-candidate predictions differed from the saved values by at most `5.56e-17` in this environment.
- This pilot uses five ridge models, not the synopsis's complete planned mixture of predictor types. Its range widths are fixed within each round and are not scaled by model disagreement. Reuse of the same 20 range-setting examples, adaptive choices, one random seed and one dataset limit interpretation. No repair, language model, detector, repeated-seed uncertainty study or final comparison is implemented.
