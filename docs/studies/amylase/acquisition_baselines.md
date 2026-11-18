<div align="center">

# Uncertainty-guided comparison: development protocol

Protocol and findings

</div>

## Protocol

Recorded before running the comparisons on 16 November 2026. These are exploratory amylase development runs, not a final evaluation or a claim of Bayesian guarantees.

The existing five-predictor group gives each candidate a mean prediction `m` and a spread `s`, the standard deviation across members. Treating this spread as if it were a Gaussian predictive standard deviation is a working approximation: these bootstrap ridge members are not a Bayesian posterior and their spread has not been shown calibrated.

Compare two finite-pool selection rules with the previously recorded matched seed-13 greedy run. Upper-confidence selection ranks `m + s`, using a fixed multiplier of one. Gaussian expected improvement ranks the expected positive difference between a hypothetical `Normal(m, s)` score and the best score already revealed, with no additional exploration offset. For `s = 0`, it reduces to `max(m - best, 0)`. Within a batch, rank all candidates once; break ties by identifier. This simple batch construction does not update the predictor between choices and does not model dependencies among simultaneous selections.

Use seed 13, role seed 2013, member seed 3013, the same eligible pool, 100 starting observations, maximum 100 new measurements and batches of ten. Save all candidate acquisition scores and model predictions before revealing each batch. Do not provide hidden scores, original split labels, the pool optimum or top-1% membership to the selector. Compute finite-pool comparison metrics only after both new runs finish, using the existing independent evaluation boundary. Include all completed runs and report failures and actual stops.

Check the acquisition formulas on small examples, zero spread, invalid values and deterministic ties. Independently reconstruct the recorded acquisition values and rankings from saved means and spreads, check initial and role assignments against the existing greedy record, and verify score reveals, budget and summary metrics. These comparisons concern one protein and one seed; results do not establish broad performance or a validated uncertainty measure. The choice of a mean-and-uncertainty acquisition rule is discussed in [Greenman et al.](https://pmc.ncbi.nlm.nih.gov/articles/PMC11741572/); the normal expected-improvement assumption is described in the [scikit-optimize documentation](https://scikit-optimize.github.io/stable/modules/generated/skopt.acquisition.gaussian_ei.html).

## Findings

Completed 16 November 2026 under the [predeclared protocol](acquisition_baselines.md#protocol). These are two exploratory runs on the same amylase seed used in the [matched comparison](matched_reward_comparison.md#findings).

| Selection rule | New measurements | Best observed score | Gap from eligible-pool maximum | Saved ranges covered |
| --- | ---: | ---: | ---: | ---: |
| Mean prediction plus member spread | 100 | 0.19428 | 0.01735 | 100/100 |
| Gaussian expected improvement | 100 | 0.18432 | 0.02732 | 100/100 |
| Earlier matched greedy prediction | 100 | 0.18225 | 0.02938 | 100/100 |

All three started with a best score of 0.18225, already above the eligible pool's top-1% threshold. The maximum recorded score in the eligible pool was 0.21163. The two new runs used the same 100 starting measurements, 20 range-setting examples, model seeds, available pool and budget as the earlier greedy run. Each exhausted the 100-new-measurement budget.

The first rule adds one times the spread across the five models to their mean. The second calculates expected improvement by **assuming** a normal distribution whose mean and standard deviation equal the model mean and spread. These are finite-pool, batch approximations: the members are bootstrapped ridge models rather than a Bayesian posterior, spread is not established as calibrated, and the batch choices are not updated one by one. The labels “upper confidence” and “expected improvement” describe the selection formulas, not a validated confidence guarantee.

An independent audit recalculated every acquisition score using a separate normal-distribution implementation, checked each top-ten selection, matched initial and reserved examples, checked source measurements and budgets, and verified lossless record compression. The new runs' range coverage was 100/100 with mean widths about 0.238 and 0.245 respectively; this does not guarantee future coverage. The records and hashes are in [upper-confidence output](../../../output/amylase/search/amylase_acquisition_ucb_seed13), [expected-improvement output](../../../output/amylase/search/amylase_acquisition_ei_seed13) and [the comparison summary](../../../output/amylase/search/amylase_acquisition_comparison_seed13).

All 65 backend tests passed, including zero spread, invalid values, deterministic ties and a synthetic run that checks acquisition scores are recorded before selection. This one-seed result does not establish a general winner, quantify uncertainty across independent biological datasets, or validate the repair system. Genetic and AdaLead-style baselines, repeated matched comparisons and the remaining evaluation datasets are still required.

To run either rule with a new output directory:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend:. python3 -m scripts.amylase.run_prediction_pilot output/my-ucb --seed 13 --role-seed 2013 --member-seed 3013 --acquisition ucb
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend:. python3 -m scripts.amylase.run_prediction_pilot output/my-ei --seed 13 --role-seed 2013 --member-seed 3013 --acquisition ei
```
