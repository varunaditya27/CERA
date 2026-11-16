# Matched reward comparison: development protocol

Recorded before running this comparison on 16 November 2026. This is an exploratory amylase development check, not a final evaluation of CERA or a test on IRED or Hydro. The warning and repair rules remain provisional.

## Question and methods

Does the current warning-and-repair loop behave differently from simpler approaches when all receive the same initial measurements and maximum new-measurement budget? The first comparison uses initial seed 13, the same 100 initial observations, all eligible measured amylase candidates, a four-substitution limit, batches of ten and a maximum of 100 new measurements. It includes:

1. Random sampling from the eligible unqueried pool using seed `1000 + 13`.
2. Greedy selection using the existing five-predictor group and mean prediction, retrained every round; the three reward weights are zero.
3. The fixed example reward, using the same predictor and retraining schedule, with no warning-driven changes.
4. The same initial reward and retraining schedule with the current rule-based warning and repair system.

For the three model-based methods, assign the 20 range-setting examples with seed `2000 + 13` and generate member seeds with `3000 + 13`. The model-assisted repair variant is not included in this first comparison; its hosted calls and potential fallbacks require separate accounting. The initial example reward is the checked-in [specification](reward_spec_example.json). These are development settings, not selected optimal values.

## Measurement and evaluation

Each selector accesses only the supported measurement interface. Separately, after **all** methods have finished, an evaluator may use all eligible source scores to calculate the best available measured score in this finite pool. The evaluator checks source fingerprints, initial measurements, selection/reveal chronology, uniqueness, budget and stop reason. Pool optimum and top-1% membership must never enter a selector or repair input.

At the start and after every completed batch report: actual new-measurement count, best score observed including the starting set, and the gap between the eligible pool's maximum recorded score and that best observed score. This gap is finite-pool simple regret, not a biological global optimum. Define the top 1% as at least the score of the `ceil(0.01 * eligible_count)`-th highest eligible variant, including ties, and report whether the best observed score meets it. Preserve early stopping explicitly; do not pad a stopped run as if it used additional measurements. Report actual stops and failures, not just successful runs.

Predicted range coverage and width are available only for the three model-based methods and should retain their actual denominators. Random sampling has no prediction ranges in this comparison, so coverage is unavailable rather than zero. Paired seeds improve comparability but one matched set cannot support statistical significance or a general biological conclusion. A protein-engineering benchmark found that uncertainty-based optimization did not consistently beat greedy selection, reinforcing the need for simple comparisons ([Greenman et al.](https://pmc.ncbi.nlm.nih.gov/articles/PMC11741572/)).

## Checks and limits

Before interpreting results, independently verify that all methods started with identical IDs and scores and identical data, reference, mutation cap and total budget; check the model-based role assignments and initial settings; reconstruct summaries from complete records and source scores; verify no duplicates or budget overruns; and report the actual last measurement count and stop for each method. Preserve full run records with fingerprints. This first check does not establish precision, repair recovery, biological replication or warning accuracy. Additional seeds, model-assisted repair, the other required baselines and separate evaluation datasets remain required.
