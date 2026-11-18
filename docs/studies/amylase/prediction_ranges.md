<div align="center">

# Prediction ranges

Plan and findings

</div>

## Plan

Status: implemented for one exploratory amylase pilot after Varun's approval. This stage tests the machinery; it is not a completed CERA repair or final evaluation. See the [pilot findings](prediction_ranges.md#findings). It builds on the [amylase protocol](development_protocol.md), [ESM feasibility record](../../background/esm_feasibility.md), and [implementation research notes](../../background/implementation_notes.md).

### What this stage is for

A predictor estimates a variant's score using its numerical sequence representation. A predictor group, often called an ensemble, combines several independently fitted predictors. Their spread is a possible uncertainty signal, not proof that the group's predictions are reliable. A prediction range is an interval intended to contain a later score. The purpose here is to record those ranges before measurements are revealed and measure their observed coverage and width.

### Data rules

- Keep the approved all-eligible candidate pool, four-substitution amylase development constraint, initial set and measurement budget. Use the existing score-free representation cache, verify its dataset/reference/model fingerprints and ordered identifiers against independent expectations, and join by sequence identifier. The cache has all 3,706 amylase sequences; eligibility remains the runner's responsibility.
- From each run's 100 starting measurements, keep the existing reproducibly chosen 20 reserved for range setting and 80 for predictor fitting and model selection. Newly revealed scores may enter later fitting only after their predictions and ranges have been saved and their measurements revealed. Do not use reserved scores to choose model settings or to claim independent coverage.
- Model fitting sees only permitted scores. The evaluator uses already-revealed scores and saved pre-reveal intervals to calculate how many were covered and their widths. Original split labels are joined only after selection for reporting.

### Proposed first predictor group

Use five ridge predictors on the fixed ESM-2 representations for this development step. Ridge regression is a linear scoring model that limits overly large fitted weights. Five is the lower end of the synopsis's proposed group size, not a proven optimum. This initial group does **not** implement the synopsis's planned neural-network members or establish the final ensemble design.

For each batch, choose the ridge penalty using cross-validation on the original fitting examples available at that point. Cross-validation fits on part of those examples and checks on another part, rotating the held-out portion. Only after choosing the penalty, create five independently seeded bootstrap samples of the fitting examples (sampling with replacement) and fit one member to each. This ordering prevents duplicate copies of one observation from falling on both sides of a cross-validation fold. Record the penalty, sampling seeds, fitting identifiers, versions and cache fingerprint. If learned scaling is introduced, fit it inside each cross-validation training fold and separately for final members, never on reserved or future scores. Do not assume disagreement among these members is calibrated uncertainty. [Deep ensembles](https://proceedings.neurips.cc/paper_files/paper/2017/hash/9ef2ed4b7fd2c810847ffa5fa85bce38-Abstract.html); [leakage guidance](https://scikit-learn.org/stable/common_pitfalls.html#data-leakage).

### First prediction ranges

Use the mean of member predictions as the point prediction and their standard deviation as a separately reported disagreement signal. For a simple initial range, calculate the absolute errors on the 20 reserved examples and use the standard split-conformal finite-sample order statistic for a nominal 90% target: sort the 20 errors and select the 19th smallest. Add and subtract that error from each point prediction. Ties must be handled consistently, and insufficient calibration samples or non-finite values must not silently produce a misleading interval. [Split-conformal formulation](https://www.stat.berkeley.edu/~ryantibs/papers/weightedcp-supp.pdf).

These are symmetric constant-width ranges within a round; the ensemble spread is **not** the range width. Ordinary coverage guarantees depend on assumptions that adaptive selection and repeated use of the reserved examples can violate. Therefore the 90% value is a nominal target, not a guarantee. Reusing a fixed reserved set while later fitting data were adaptively chosen can create indirect dependence even if the reserved scores are never passed directly to fitting. [Feedback shift in biomolecular design](https://pmc.ncbi.nlm.nih.gov/articles/PMC9618043/).

Select the next batch by highest mean prediction for this initial pilot, without an uncertainty penalty or repair. Record each candidate's mean, member spread and range **before** revealing the selected scores. In each revealed batch and cumulatively, calculate the number covered, denominator, coverage and mean range width. Small batches produce coarse, noisy coverage measurements. Save actual selections and stop reasons; never manufacture values after an early stop.

### Implementation and verification plan

1. Add focused modules for the representation-based predictor group and interval calculation; reuse the existing runner and cache, and keep the catalog separate. Verify installed APIs against the pinned packages.
2. Extend the run record to validate and save predictions, member spread and bounds before revealing scores, without exposing hidden scores. Retain current random and one-hot comparison behavior.
3. Test with invented data: no reserved score enters tuning or fitting; bootstrap reproducibility; no duplicates cross cross-validation folds; exact conformal ranks and ties; insufficient/non-finite inputs; pre-reveal record order; cache mismatch rejection; and reconstruction of coverage and widths from saved events. Check unchanged runner/catalog behavior.
4. After tests pass, run one exploratory amylase pilot with a recorded seed and preserve its full record. Recompute coverage and widths from the record independently. Document starting examples, settings, runtime and limitations. Consider repeated runs only after the pilot's behavior has been inspected; do not tune against IRED or Hydro.

The next stage does not implement warning detectors, repairs, language-model integration, or a final research comparison. A graph may help explain the results, but source tables and records remain necessary for independent checking.

## Findings

Completed 16 November 2026 under the [development plan](prediction_ranges.md#plan). This single exploratory run checks the workflow, not a general coverage guarantee, a CERA repair, or a final evaluation.

### Setup

Used the pinned 3,706-sequence ESM-2 representation cache and the existing amylase runner. The initial-set seed was 1, the role-assignment seed 3, and the member-seed generator seed 4. Of 100 initial measurements, 80 were available for fitting and model selection; 20 were reserved for range setting. Each of five ridge predictors was fitted on its own reproducibly resampled fitting set after cross-validation selected a penalty on the unique fitting examples. After every batch, newly revealed measurements became available for the next fitting step. Scores of the 20 reserved examples were not passed directly to fitting or model selection.

For each round, the mean of the five predictions determined selection. The population standard deviation across members was recorded as a disagreement signal; it was not used as the range width. A symmetric range was set by the 19th smallest absolute error on the 20 reserved examples. The target was nominally 90%, but adaptive selection and reuse of range-setting data prevent assuming the standard guarantee. No uncertainty penalty, warning detector or repair was used.

Run command:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend:. python3 -m scripts.amylase.run_prediction_pilot output/amylase_range_pilot_seed1 --seed 1
```

The script reported 10 batches in 1.6667 seconds; that duration includes run creation, fitting, prediction, logging and report generation, but excludes loading and validating the cache. It is one local timing, not a benchmark. Settings, fitting identifiers, member seeds, source hashes, pre-reveal predictions, intervals and revealed scores are in [run.jsonl](../../../output/amylase_range_pilot_seed1/run.jsonl).

### Observations

All **100 of 100** selected scores fell inside their previously recorded ranges. Mean range width across those scores was approximately **0.20337** in the dataset's score units; per-batch results are in [coverage.csv](../../../output/amylase_range_pilot_seed1/coverage.csv). Broad ranges can cover many scores while providing limited precision. Ten scores per batch make each batch coverage value change in increments of ten percentage points. The observed 100% is not evidence that future coverage is guaranteed, nor that 100% is intrinsically better than a better-calibrated narrower range.

The pilot selected 66 original-train and 34 original-test variants, counted by joining original split labels after the run; these labels were not supplied to the selector. The best observed score after 100 new measurements was 0.1569333333333333. This pilot changed both representation and predictor structure relative to the earlier one-hot greedy experiment, so its movement across the split cannot be attributed to either change separately.

### Verification and limitations

- Fifteen unit tests passed, including reserved-score isolation, unique data before cross-validation, reproducible resampling, finite-sample rank and ties, invalid ranges, pre-reveal ordering, report reconstruction and cache fingerprint rejection.
- Independently audited each batch's candidate ranking, recorded fitting/reserved separation, member seed count, radius and bounds, unique queries, source scores, budget and reconstructed coverage table. All ten batches passed.
- Independently reconstructed the first round using the recorded fitting data and member seeds: the penalty was 0.1; the range-setting radius was 0.09607034487804328; selected-candidate predictions differed from the saved values by at most `5.56e-17` in this environment.
- This pilot uses five ridge models, not the synopsis's complete planned mixture of predictor types. Its range widths are fixed within each round and are not scaled by model disagreement. Reuse of the same 20 range-setting examples, adaptive choices, one random seed and one dataset limit interpretation. No repair, language model, detector, repeated-seed uncertainty study or final comparison is implemented.
