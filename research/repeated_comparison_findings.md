# Repeated amylase comparison: development findings

Run and checked 16 November 2026 using the [predeclared protocol](repeated_comparison_protocol.md). These are exploratory comparisons on one existing dataset, not CERA repair results or evidence of performance on other proteins.

## What happened

Ten paired comparisons used starting-set seeds 2 through 11. Within each pair, both methods started with the same 100 known examples and were allowed 100 new measurements. The greedy predictor achieved a higher final best-observed score in 9 pairs; random selection did so in 1; there were no ties. The mean of the ten paired differences (greedy minus random) was 0.010955 in the source score's units. This average describes these runs only; no confidence interval or general claim is established.

The strongest behavioral difference is where the methods searched. In every pair the greedy predictor selected all 100 variants from the original training side and none from the original shifted test side. Random selection chose 49 to 61 test-side variants per pair. The labels used for this count were joined from the original CSV after the runs and were not provided to the selectors. These observations do not prove why the greedy method favored the training side. Since the primary pool includes both sides, the comparison does not guarantee that a method experiences the intended position shift.

The complete paired scores, differences and split counts are in [summary.csv](../output/amylase_repeated/summary.csv); full per-run records and best-so-far tables are in the adjacent `seed_02` through `seed_11` directories. The earlier seed-1 run is not included in these ten pairs because it used different random-seed assignments.

## How the results were checked

For every pair, an independent post-run audit checked matching starting measurements, dataset and reference fingerprints, candidate constraints and budget; the recorded random seeds and 20 reserved identifiers; ten selections and ten reveals; no repeat queries; all revealed measurements against the source CSV; pre-reveal greedy predictions and descending ranking; remaining-budget arithmetic; budget-exhaustion status; and each best-so-far CSV against the run log. The audit also checked the number of predictions against the remaining eligible pool. All checks passed for ten pairs and 200 method-batches.

The ten pairs were run through the existing Python interface with `seed` from 2 through 11, `selection_seed=1000+seed`, and `role_seed=2000+seed`. Thread limits were `OPENBLAS_NUM_THREADS=1` and `OMP_NUM_THREADS=1`; `PYTHONPATH=backend`. Each run record contains software versions and fingerprints of its source modules. A stopped or partial record would not be counted as a successful completed pair.

## Interpretation and next questions

- Repeated starting sets on one fixed dataset do not represent ten independent protein datasets. Counts of wins are descriptive; they are not proof of statistical or biological generality.
- The current predictor has no calibration, uncertainty intervals, warning detectors or repairs. Its success at finding high observed scores within this pool says nothing yet about whether CERA repairs improve search.
- Understand the apparent reluctance to choose shifted-side variants before drawing conclusions. Analyze the model's pre-reveal rankings, sequence changes and training support on amylase without using IRED or Hydro to tune choices. Distinguish evidence from any causal hypothesis.
- The initial development protocol reserves 20 known examples from predictor fitting, although no interval method exists yet; comparison results are conditional on that allocation. The random selector does not need those scores, but both methods receive the same starting measurements.

## Follow-up inspection of the first selection round

This inspection was conducted after seeing the repeated results and is exploratory, not predeclared. For each run, compare the saved pre-reveal predictions of all candidates grouped by their original split, and compare sequence changes against the 80 starting fitting examples. Group labels were joined after the runs for analysis only.

- The median predicted score for original-test candidates exceeded the median for original-train candidates in all ten first rounds. Nevertheless, the selected top ten in each first round were all original-train candidates. A higher median does not imply the highest individual predictions belong to that group.
- In every first round, 1,708 of 1,709 original-test candidates contained at least one specific position-and-letter change not present in the 80 starting fitting sequences. The one without such a change is the reference sequence. Among original-train candidates, the corresponding counts ranged from 1,268 to 1,327 out of 1,466.
- These counts characterize training support, not the true fitness of those candidates. They do not prove that unfamiliar substitutions caused the selection pattern. The model can combine seen and unseen features, and we have not yet isolated their effects or tested alternative selection rules.
