<div align="center">

# Repeated amylase development comparison

Protocol and findings

</div>

## Protocol

Recorded before the repeated runs on 16 November 2026. This is exploratory development on amylase, not the final CERA evaluation. The existing [first comparison plan](first_comparison.md) and [amylase development protocol](development_protocol.md) still apply.

### Motivation

In the first exploratory run, random selection queried 49 original-train and 51 original-test variants; the greedy predictor queried 100 original-train and zero original-test variants. These counts were calculated after the run from its identifiers and the source file. They show where each method searched; they do not establish why it chose those variants. Do not feed the original split labels or unqueried scores back into selection.

### Predeclared runs

- Run ten matched pairs with initial-set seeds 2 through 11 inclusive. Both methods within each pair receive the same initial set, source data, candidate constraints and maximum budget.
- Use selection seed 1000 plus the initial seed, and data-role seed 2000 plus the initial seed; the predictor's cross-validation seed equals the initial-set seed. These are recorded in each run. Do not choose seeds after seeing results.
- Use the existing implementation without changing method settings in response to these runs. Each pair retains complete selection, prediction and measurement records and score tables. The earlier seed-1 run is separate because its selection and role seeds differ.
- Check each pair's matching initial data and settings, selection/reveal order, unique queries, budget accounting, summary reconstruction and greedy ranking. Report failures and incomplete runs rather than excluding them silently.
- Report all per-pair final best scores and differences, plus original split counts of newly selected variants. Record the number of pairs where each method's final best score is greater or tied. Do not call the runs independent biological datasets or treat ten batches in a run as ten repetitions. Do not infer broad significance or a general biological winner from ten runs on one dataset. [Paired comparisons](https://www.itl.nist.gov/div898/handbook/prc/section3/prc311.htm); [randomness and reproducibility in model comparisons](https://proceedings.mlr.press/v97/bouthillier19a.html).

The current runner keeps selection and role seeds fixed by default when called through its command-line script; these runs explicitly supply the seeds through its existing Python interface. Nothing here claims calibration, failure detection or repair has been implemented.

## Findings

Run and checked 16 November 2026 using the [predeclared protocol](repeated_comparison.md#protocol). These are exploratory comparisons on one existing dataset, not CERA repair results or evidence of performance on other proteins.

### What happened

Ten paired comparisons used starting-set seeds 2 through 11. Within each pair, both methods started with the same 100 known examples and were allowed 100 new measurements. The greedy predictor achieved a higher final best-observed score in 9 pairs; random selection did so in 1; there were no ties. The mean of the ten paired differences (greedy minus random) was 0.010955 in the source score's units. This average describes these runs only; no confidence interval or general claim is established.

The strongest behavioral difference is where the methods searched. In every pair the greedy predictor selected all 100 variants from the original training side and none from the original shifted test side. Random selection chose 49 to 61 test-side variants per pair. The labels used for this count were joined from the original CSV after the runs and were not provided to the selectors. These observations do not prove why the greedy method favored the training side. Since the primary pool includes both sides, the comparison does not guarantee that a method experiences the intended position shift.

The complete paired scores, differences and split counts are in [summary.csv](../../../output/amylase/search/amylase_repeated/summary.csv); full per-run records and best-so-far tables are in the adjacent `seed_02` through `seed_11` directories. The earlier seed-1 run is not included in these ten pairs because it used different random-seed assignments.

### How the results were checked

For every pair, an independent post-run audit checked matching starting measurements, dataset and reference fingerprints, candidate constraints and budget; the recorded random seeds and 20 reserved identifiers; ten selections and ten reveals; no repeat queries; all revealed measurements against the source CSV; pre-reveal greedy predictions and descending ranking; remaining-budget arithmetic; budget-exhaustion status; and each best-so-far CSV against the run log. The audit also checked the number of predictions against the remaining eligible pool. All checks passed for ten pairs and 200 method-batches.

The ten pairs were run through the existing Python interface with `seed` from 2 through 11, `selection_seed=1000+seed`, and `role_seed=2000+seed`. Thread limits were `OPENBLAS_NUM_THREADS=1` and `OMP_NUM_THREADS=1`; `PYTHONPATH=backend`. Each run record contains software versions and fingerprints of its source modules. A stopped or partial record would not be counted as a successful completed pair.

### Interpretation and next questions

- Repeated starting sets on one fixed dataset do not represent ten independent protein datasets. Counts of wins are descriptive; they are not proof of statistical or biological generality.
- The current predictor has no calibration, uncertainty intervals, warning detectors or repairs. Its success at finding high observed scores within this pool says nothing yet about whether CERA repairs improve search.
- Understand the apparent reluctance to choose shifted-side variants before drawing conclusions. Analyze the model's pre-reveal rankings, sequence changes and training support on amylase without using IRED or Hydro to tune choices. Distinguish evidence from any causal hypothesis.
- The initial development protocol reserves 20 known examples from predictor fitting, although no interval method exists yet; comparison results are conditional on that allocation. The random selector does not need those scores, but both methods receive the same starting measurements.

### Follow-up inspection of the first selection round

This inspection was conducted after seeing the repeated results and is exploratory, not predeclared. For each run, compare the saved pre-reveal predictions of all candidates grouped by their original split, and compare sequence changes against the 80 starting fitting examples. Group labels were joined after the runs for analysis only.

- The median predicted score for original-test candidates exceeded the median for original-train candidates in all ten first rounds. Nevertheless, the selected top ten in each first round were all original-train candidates. A higher median does not imply the highest individual predictions belong to that group.
- In every first round, 1,708 of 1,709 original-test candidates contained at least one specific position-and-letter change not present in the 80 starting fitting sequences. The one without such a change is the reference sequence. Among original-train candidates, the corresponding counts ranged from 1,268 to 1,327 out of 1,466.
- These counts characterize training support, not the true fitness of those candidates. They do not prove that unfamiliar substitutions caused the selection pattern. The model can combine seen and unseen features, and we have not yet isolated their effects or tested alternative selection rules.

### Follow-up inspection of ranking and fitted weights

This is also a post-hoc analysis, performed on 16 November using the existing records; it did not alter the runs. Candidates are ranked by the saved prediction and then identifier, as in the selector. Original train/test labels were joined only for this inspection.

- In the first round, the highest-ranked original-test candidate was between rank 313 and rank 492 across the ten runs; its median rank was 368. A lower rank means a higher prediction. The selected batch contains the top ten.
- Across all 100 greedy selection rounds in the ten runs, the highest-ranked test candidate was never above rank 102. The median of these 100 ranks was 249.5. These ranks are repeated decisions within related runs, not 100 independent experiments.
- Reconstructed the first-round model for seed 2 using its recorded initial examples, reserved identifiers, cross-validation seed and penalty choices. On 100 candidate sequences, its predictions matched the saved values exactly in the current environment. The one-hot representation has 8,500 possible position-and-letter indicators. Of these, 7,904 never occurred in the 80 fitting sequences; their fitted ridge coefficients were all exactly zero. This is a property of this fit, not a direct measurement of whether any candidate is good or bad.
- A previously unseen substitution can therefore have no independently learned coefficient in this simple model. Scores still combine the intercept and all other position-and-letter indicators. The result does not prove that zero coefficients caused the lack of shifted-side selection; a controlled comparison or direct decomposition is needed to support that claim. Do not treat the absence of selection as proof of poor real-world performance.

### Exploratory representation-distance check

After the ESM-2 cache was generated, measured Euclidean distance in the 320-number representation from each first-round candidate to its nearest member of the 80-example fitting set. Euclidean distance is ordinary straight-line distance between numerical vectors; it is not a count of amino-acid substitutions. Original split labels were joined only after the earlier selections. In all ten runs, the median distance for original-test candidates exceeded that for original-train candidates: train medians ranged approximately 0.06027–0.06278 and test medians 0.07365–0.07623. This is a post-hoc description of one checkpoint, pooling choice and dataset, not an established warning threshold or proof of prediction error. Cache contents and ordered identifiers were validated; the comparison used the cache's recorded settings and did not re-run the model.
