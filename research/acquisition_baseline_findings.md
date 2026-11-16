# Uncertainty-guided baseline development runs

Completed 16 November 2026 under the [predeclared protocol](acquisition_baseline_protocol.md). These are two exploratory runs on the same amylase seed used in the [matched comparison](matched_reward_comparison_findings.md).

| Selection rule | New measurements | Best observed score | Gap from eligible-pool maximum | Saved ranges covered |
| --- | ---: | ---: | ---: | ---: |
| Mean prediction plus member spread | 100 | 0.19428 | 0.01735 | 100/100 |
| Gaussian expected improvement | 100 | 0.18432 | 0.02732 | 100/100 |
| Earlier matched greedy prediction | 100 | 0.18225 | 0.02938 | 100/100 |

All three started with a best score of 0.18225, already above the eligible pool's top-1% threshold. The maximum recorded score in the eligible pool was 0.21163. The two new runs used the same 100 starting measurements, 20 range-setting examples, model seeds, available pool and budget as the earlier greedy run. Each exhausted the 100-new-measurement budget.

The first rule adds one times the spread across the five models to their mean. The second calculates expected improvement by **assuming** a normal distribution whose mean and standard deviation equal the model mean and spread. These are finite-pool, batch approximations: the members are bootstrapped ridge models rather than a Bayesian posterior, spread is not established as calibrated, and the batch choices are not updated one by one. The labels “upper confidence” and “expected improvement” describe the selection formulas, not a validated confidence guarantee.

An independent audit recalculated every acquisition score using a separate normal-distribution implementation, checked each top-ten selection, matched initial and reserved examples, checked source measurements and budgets, and verified lossless record compression. The new runs' range coverage was 100/100 with mean widths about 0.238 and 0.245 respectively; this does not guarantee future coverage. The records and hashes are in [upper-confidence output](../output/amylase_acquisition_ucb_seed13/), [expected-improvement output](../output/amylase_acquisition_ei_seed13/) and [the comparison summary](../output/amylase_acquisition_comparison_seed13/).

All 65 backend tests passed, including zero spread, invalid values, deterministic ties and a synthetic run that checks acquisition scores are recorded before selection. This one-seed result does not establish a general winner, quantify uncertainty across independent biological datasets, or validate the repair system. Genetic and AdaLead-style baselines, repeated matched comparisons and the remaining evaluation datasets are still required.

To run either rule with a new output directory:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend python3 scripts/run_prediction_pilot.py output/my-ucb --seed 13 --role-seed 2013 --member-seed 3013 --acquisition ucb
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend python3 scripts/run_prediction_pilot.py output/my-ei --seed 13 --role-seed 2013 --member-seed 3013 --acquisition ei
```
