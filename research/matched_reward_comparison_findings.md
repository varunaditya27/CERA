# First matched reward comparison

Run 16 November 2026 under the [predeclared development protocol](matched_reward_comparison_protocol.md). This is one matched amylase starting set, not an independent biological replication or a final evaluation.

| Method | New measurements | Best observed score | Gap from eligible-pool maximum | Stop |
| --- | ---: | ---: | ---: | --- |
| Random | 100 | 0.19428 | 0.01735 | Budget exhausted |
| Greedy predicted score | 100 | 0.18225 | 0.02938 | Budget exhausted |
| Fixed reward | 100 | 0.18225 | 0.02938 | Budget exhausted |
| Rule-based repair | 20 | 0.18225 | 0.02938 | Two failed repairs |

The best eligible measured score in this finite pool is 0.21163. The shared initial set already contained the score 0.18225, above the pool's top-1% threshold of 0.1728, so every method met that criterion before making a new measurement. Random selection improved on the initial best in this one run; the other three did not. These observations do not establish an overall winner. The repair run stopped early and its 80 unused measurements are not counted as spent.

The greedy and fixed runs' saved prediction ranges covered 100/100 newly revealed scores. The repair run covered 20/20 before stopping. Random selection did not generate ranges, so its coverage and width are unavailable. These observations do not guarantee coverage under adaptive selection and do not measure warning or repair accuracy.

An independent audit checked the matching initial examples, data and reference fingerprints, budget, role and member seeds, unique selections, source measurements, early stop, finite-pool optimum, summary scores, range counts and widths. The complete compressed records, per-batch curves, summary and fingerprints are in [the output directory](../output/amylase_matched_reward_seed13/). The backend suite passed 61 tests. The evaluator sees all eligible scores only after every selector has finished; the selectors do not receive the optimum or top-1% threshold.

The experiment can be reproduced from the project root with a new output directory:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend python3 scripts/compare_reward_methods.py output/my-matched-comparison --seed 13
```

The script preserves failed method status and partial records if a method fails. Further seeds, the other required baselines, model-assisted repair and evaluation on other proteins remain to be completed. These development results cannot validate a repair or establish generalization.
