# Finite-pool evolutionary baseline development runs

Completed 16 November 2026 under the [predeclared protocol](local_search_baselines_protocol.md). Both methods are adaptations to the fixed measured pool, not exact implementations of unrestricted genetic search or AdaLead. These are one-seed amylase development results.

| Method | New measurements | Best observed score | Gap from eligible-pool maximum | Saved ranges covered | Stop |
| --- | ---: | ---: | ---: | ---: | --- |
| Recombination and one mutation | 100 | 0.21163 | 0.00000 | 97/100 | Budget exhausted |
| AdaLead-style two-step search | 14 | 0.18690 | 0.02473 | 11/14 | No eligible neighbors |
| Earlier matched greedy prediction | 100 | 0.18225 | 0.02938 | 100/100 | Budget exhausted |

The recombination-based method found the highest recorded score in this eligible finite pool. The AdaLead-style method measured batches of 10, 3 and 1, then had no permitted nearby candidates; it stopped with 86 of 100 new measurements unspent. The shared initial best was 0.18225, already in the pool's top 1%. The results do not establish a general winner or that these methods would behave similarly with unmeasured variants, another seed or another protein. Coverage observations do not establish future coverage.

The genetic adaptation takes the top ten previously measured parents, forms all unique single-crossover sequences and selects measured-pool candidates at most one substitution from those sequences and at most two from a parent. Intermediates are not measured or assigned ground-truth scores. The AdaLead-style adaptation uses up to ten parents within 5% of the best measured score, considers measured-pool one-step neighbors, and expands a second step only when the intermediate's prediction is at least its parent's prediction. This replaces the original algorithm's randomized proposal rollouts with an exhaustive, bounded neighborhood. Its sparse-pool stop is therefore a property of this adaptation and dataset, not a failure rate for [the original AdaLead algorithm](https://github.com/samsinai/FLEXS/blob/master/flexs/baselines/explorers/adalead.py).

An independent audit used mutation-position dictionaries rather than the implementation's distance matrix to reconstruct every parent set, proposal set and selected ordering, including the final empty neighborhood. It also checked the shared initial and range-setting examples, model seed assignments, source scores, budget and stop. Full compressed records and hashes are in [recombination output](../output/amylase_local_genetic_seed13/), [AdaLead-style output](../output/amylase_local_adalead_seed13/) and [the comparison summary](../output/amylase_local_comparison_seed13/). All 71 backend tests passed, including rollout gating, negative-score parent thresholds, ties, invalid overlap, no-neighbor stopping and preserving the unspent budget.

Reproduce with new output directories:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend python3 scripts/run_prediction_pilot.py output/my-genetic --seed 13 --role-seed 2013 --member-seed 3013 --local-search genetic
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend python3 scripts/run_prediction_pilot.py output/my-adalead --seed 13 --role-seed 2013 --member-seed 3013 --local-search adalead
```

Further seeds, fair comparisons across all intended methods, and evaluation on the remaining proteins are still needed. These results do not validate CERA's warnings or repairs.
