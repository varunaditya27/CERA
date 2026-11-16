# Predictor group and prediction-range development plan

Status: implemented for one exploratory amylase pilot after Varun's approval. This stage tests the machinery; it is not a completed CERA repair or final evaluation. See the [pilot findings](prediction_range_pilot_findings.md). It builds on the [amylase protocol](amylase_development_protocol.md), [ESM feasibility record](esm_feasibility_and_plan.md), and [implementation research notes](implementation_research_notes.md).

## What this stage is for

A predictor estimates a variant's score using its numerical sequence representation. A predictor group, often called an ensemble, combines several independently fitted predictors. Their spread is a possible uncertainty signal, not proof that the group's predictions are reliable. A prediction range is an interval intended to contain a later score. The purpose here is to record those ranges before measurements are revealed and measure their observed coverage and width.

## Data rules

- Keep the approved all-eligible candidate pool, four-substitution amylase development constraint, initial set and measurement budget. Use the existing score-free representation cache, verify its dataset/reference/model fingerprints and ordered identifiers against independent expectations, and join by sequence identifier. The cache has all 3,706 amylase sequences; eligibility remains the runner's responsibility.
- From each run's 100 starting measurements, keep the existing reproducibly chosen 20 reserved for range setting and 80 for predictor fitting and model selection. Newly revealed scores may enter later fitting only after their predictions and ranges have been saved and their measurements revealed. Do not use reserved scores to choose model settings or to claim independent coverage.
- Model fitting sees only permitted scores. The evaluator uses already-revealed scores and saved pre-reveal intervals to calculate how many were covered and their widths. Original split labels are joined only after selection for reporting.

## Proposed first predictor group

Use five ridge predictors on the fixed ESM-2 representations for this development step. Ridge regression is a linear scoring model that limits overly large fitted weights. Five is the lower end of the synopsis's proposed group size, not a proven optimum. This initial group does **not** implement the synopsis's planned neural-network members or establish the final ensemble design.

For each batch, choose the ridge penalty using cross-validation on the original fitting examples available at that point. Cross-validation fits on part of those examples and checks on another part, rotating the held-out portion. Only after choosing the penalty, create five independently seeded bootstrap samples of the fitting examples (sampling with replacement) and fit one member to each. This ordering prevents duplicate copies of one observation from falling on both sides of a cross-validation fold. Record the penalty, sampling seeds, fitting identifiers, versions and cache fingerprint. If learned scaling is introduced, fit it inside each cross-validation training fold and separately for final members, never on reserved or future scores. Do not assume disagreement among these members is calibrated uncertainty. [Deep ensembles](https://proceedings.neurips.cc/paper_files/paper/2017/hash/9ef2ed4b7fd2c810847ffa5fa85bce38-Abstract.html); [leakage guidance](https://scikit-learn.org/stable/common_pitfalls.html#data-leakage).

## First prediction ranges

Use the mean of member predictions as the point prediction and their standard deviation as a separately reported disagreement signal. For a simple initial range, calculate the absolute errors on the 20 reserved examples and use the standard split-conformal finite-sample order statistic for a nominal 90% target: sort the 20 errors and select the 19th smallest. Add and subtract that error from each point prediction. Ties must be handled consistently, and insufficient calibration samples or non-finite values must not silently produce a misleading interval. [Split-conformal formulation](https://www.stat.berkeley.edu/~ryantibs/papers/weightedcp-supp.pdf).

These are symmetric constant-width ranges within a round; the ensemble spread is **not** the range width. Ordinary coverage guarantees depend on assumptions that adaptive selection and repeated use of the reserved examples can violate. Therefore the 90% value is a nominal target, not a guarantee. Reusing a fixed reserved set while later fitting data were adaptively chosen can create indirect dependence even if the reserved scores are never passed directly to fitting. [Feedback shift in biomolecular design](https://pmc.ncbi.nlm.nih.gov/articles/PMC9618043/).

Select the next batch by highest mean prediction for this initial pilot, without an uncertainty penalty or repair. Record each candidate's mean, member spread and range **before** revealing the selected scores. In each revealed batch and cumulatively, calculate the number covered, denominator, coverage and mean range width. Small batches produce coarse, noisy coverage measurements. Save actual selections and stop reasons; never manufacture values after an early stop.

## Implementation and verification plan

1. Add focused modules for the representation-based predictor group and interval calculation; reuse the existing runner and cache, and keep the catalog separate. Verify installed APIs against the pinned packages.
2. Extend the run record to validate and save predictions, member spread and bounds before revealing scores, without exposing hidden scores. Retain current random and one-hot comparison behavior.
3. Test with invented data: no reserved score enters tuning or fitting; bootstrap reproducibility; no duplicates cross cross-validation folds; exact conformal ranks and ties; insufficient/non-finite inputs; pre-reveal record order; cache mismatch rejection; and reconstruction of coverage and widths from saved events. Check unchanged runner/catalog behavior.
4. After tests pass, run one exploratory amylase pilot with a recorded seed and preserve its full record. Recompute coverage and widths from the record independently. Document starting examples, settings, runtime and limitations. Consider repeated runs only after the pilot's behavior has been inspected; do not tune against IRED or Hydro.

The next stage does not implement warning detectors, repairs, language-model integration, or a final research comparison. A graph may help explain the results, but source tables and records remain necessary for independent checking.
