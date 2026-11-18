<div align="center">

# Matched reward comparison: development protocol

Protocol and findings

</div>

## Protocol

Recorded before running this comparison on 16 November 2026. This is an exploratory amylase development check, not a final evaluation of CERA or a test on IRED or Hydro. The warning and repair rules remain provisional.

### Question and methods

Does the current warning-and-repair loop behave differently from simpler approaches when all receive the same initial measurements and maximum new-measurement budget? The first comparison uses initial seed 13, the same 100 initial observations, all eligible measured amylase candidates, a four-substitution limit, batches of ten and a maximum of 100 new measurements. It includes:

1. Random sampling from the eligible unqueried pool using seed `1000 + 13`.
2. Greedy selection using the existing five-predictor group and mean prediction, retrained every round; the three reward weights are zero.
3. The fixed example reward, using the same predictor and retraining schedule, with no warning-driven changes.
4. The same initial reward and retraining schedule with the current rule-based warning and repair system.

For the three model-based methods, assign the 20 range-setting examples with seed `2000 + 13` and generate member seeds with `3000 + 13`. The model-assisted repair variant is not included in this first comparison; its hosted calls and potential fallbacks require separate accounting. The initial example reward is the checked-in [specification](../../../configs/reward_spec_example.json). These are development settings, not selected optimal values.

### Measurement and evaluation

Each selector accesses only the supported measurement interface. Separately, after **all** methods have finished, an evaluator may use all eligible source scores to calculate the best available measured score in this finite pool. The evaluator checks source fingerprints, initial measurements, selection/reveal chronology, uniqueness, budget and stop reason. Pool optimum and top-1% membership must never enter a selector or repair input.

At the start and after every completed batch report: actual new-measurement count, best score observed including the starting set, and the gap between the eligible pool's maximum recorded score and that best observed score. This gap is finite-pool simple regret, not a biological global optimum. Define the top 1% as at least the score of the `ceil(0.01 * eligible_count)`-th highest eligible variant, including ties, and report whether the best observed score meets it. Preserve early stopping explicitly; do not pad a stopped run as if it used additional measurements. Report actual stops and failures, not just successful runs.

Predicted range coverage and width are available only for the three model-based methods and should retain their actual denominators. Random sampling has no prediction ranges in this comparison, so coverage is unavailable rather than zero. Paired seeds improve comparability but one matched set cannot support statistical significance or a general biological conclusion. A protein-engineering benchmark found that uncertainty-based optimization did not consistently beat greedy selection, reinforcing the need for simple comparisons ([Greenman et al.](https://pmc.ncbi.nlm.nih.gov/articles/PMC11741572/)).

### Checks and limits

Before interpreting results, independently verify that all methods started with identical IDs and scores and identical data, reference, mutation cap and total budget; check the model-based role assignments and initial settings; reconstruct summaries from complete records and source scores; verify no duplicates or budget overruns; and report the actual last measurement count and stop for each method. Preserve full run records with fingerprints. This first check does not establish precision, repair recovery, biological replication or warning accuracy. Additional seeds, model-assisted repair, the other required baselines and separate evaluation datasets remain required.

## Findings

Run 16 November 2026 under the [predeclared development protocol](matched_reward_comparison.md#protocol). This is one matched amylase starting set, not an independent biological replication or a final evaluation.

| Method | New measurements | Best observed score | Gap from eligible-pool maximum | Stop |
| --- | ---: | ---: | ---: | --- |
| Random | 100 | 0.19428 | 0.01735 | Budget exhausted |
| Greedy predicted score | 100 | 0.18225 | 0.02938 | Budget exhausted |
| Fixed reward | 100 | 0.18225 | 0.02938 | Budget exhausted |
| Rule-based repair | 20 | 0.18225 | 0.02938 | Two failed repairs |

The best eligible measured score in this finite pool is 0.21163. The shared initial set already contained the score 0.18225, above the pool's top-1% threshold of 0.1728, so every method met that criterion before making a new measurement. Random selection improved on the initial best in this one run; the other three did not. These observations do not establish an overall winner. The repair run stopped early and its 80 unused measurements are not counted as spent.

The greedy and fixed runs' saved prediction ranges covered 100/100 newly revealed scores. The repair run covered 20/20 before stopping. Random selection did not generate ranges, so its coverage and width are unavailable. These observations do not guarantee coverage under adaptive selection and do not measure warning or repair accuracy.

An independent audit checked the matching initial examples, data and reference fingerprints, budget, role and member seeds, unique selections, source measurements, early stop, finite-pool optimum, summary scores, range counts and widths. The complete compressed records, per-batch curves, summary and fingerprints are in [the output directory](../../../output/amylase_matched_reward_seed13). The backend suite passed 61 tests. The evaluator sees all eligible scores only after every selector has finished; the selectors do not receive the optimum or top-1% threshold.

The experiment can be reproduced from the project root with a new output directory:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend:. python3 -m scripts.amylase.compare_reward_methods output/my-matched-comparison --seed 13
```

The script preserves failed method status and partial records if a method fails. Further seeds, the other required baselines, model-assisted repair and evaluation on other proteins remain to be completed. These development results cannot validate a repair or establish generalization.
