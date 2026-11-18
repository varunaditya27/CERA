<div align="center">

# Finite-pool evolutionary baselines: development protocol

Protocol and findings

</div>

## Protocol

Recorded before implementation and runs on 16 November 2026. These are adaptations to a fixed measured pool, not exact reproductions of unrestricted genetic search or [FLEXS AdaLead](https://github.com/samsinai/FLEXS/blob/master/flexs/baselines/explorers/adalead.py). They are exploratory amylase development comparisons.

### Shared rules

Use the same seed-13 initial measurements, seed-2013 range-setting role assignment, seed-3013 model-member generator, five-predictor group, eligible pool, four-substitution limit, batches of at most ten and maximum 100 new measurements as the earlier matched greedy run. Fit and predict on the same schedule. Rank all proposed, eligible, unqueried candidates by mean predicted score, breaking ties by identifier. Never read an unqueried score or original split label when generating or ranking proposals.

For each round choose at most ten parent variants from previously measured variants, ordered by measured score and then identifier. A proposal must be at most two residue substitutions away from at least one selected parent. If fewer than ten proposals remain, measure only those; if none exist, stop with `no_neighbors` and record unspent budget. Do not silently fill a batch with distant candidates. Counts, parent IDs and proposed IDs must be saved before measurements are revealed.

### Recombination-and-mutation baseline

Use the ten highest-scoring measured parents. Generate unique single-crossover sequences by joining the prefix of one parent and suffix of another at each informative position; include the parent sequences themselves as possible recombination outputs. No score is obtained for an intermediate sequence. A measured-pool candidate is eligible for proposal if it differs by at most one substitution from one of these recombination outputs **and** at most two substitutions from a selected parent. The full eligible finite pool is scanned rather than generating and testing arbitrary unmeasured mutations. This is a deterministic, one-generation finite-pool genetic adaptation, not a standard stochastic genetic algorithm with multiple generations.

### AdaLead-style baseline

Take up to ten highest-scoring measured parents whose score is at least `best - 0.05 * abs(best)`. For each parent, propose all unqueried measured-pool variants at distance one. Continue one more mutation step from any measured-pool one-step neighbor whose model prediction is at least the parent's model prediction; add its one-step unqueried neighbors that are within two substitutions of that original parent. Previously measured sequences may act as intermediate nodes, but only unqueried candidates can be selected. This exhaustively searches a two-step finite-pool neighborhood instead of the original algorithm's randomized rollouts and recombination, and uses model predictions for continuation, so call it AdaLead-style rather than AdaLead.

### Checks and interpretation

Test mutation distance, recombination, rollout gating, deterministic ties, repeated measurements, partial batches and empty neighborhoods on hand-checkable synthetic sequences. Independently reconstruct parent choices, proposal sets and selected rankings for all rounds; check source measurements, budgets, initial data and model seeds. Evaluate the eligible-pool optimum only after both methods have stopped, and retain complete records and failures. One run on one protein cannot establish a general winner, and the finite-pool restriction can substantially change the behavior of either method.

## Findings

Completed 16 November 2026 under the [predeclared protocol](local_search_baselines.md#protocol). Both methods are adaptations to the fixed measured pool, not exact implementations of unrestricted genetic search or AdaLead. These are one-seed amylase development results.

| Method | New measurements | Best observed score | Gap from eligible-pool maximum | Saved ranges covered | Stop |
| --- | ---: | ---: | ---: | ---: | --- |
| Recombination and one mutation | 100 | 0.21163 | 0.00000 | 97/100 | Budget exhausted |
| AdaLead-style two-step search | 14 | 0.18690 | 0.02473 | 11/14 | No eligible neighbors |
| Earlier matched greedy prediction | 100 | 0.18225 | 0.02938 | 100/100 | Budget exhausted |

The recombination-based method found the highest recorded score in this eligible finite pool. The AdaLead-style method measured batches of 10, 3 and 1, then had no permitted nearby candidates; it stopped with 86 of 100 new measurements unspent. The shared initial best was 0.18225, already in the pool's top 1%. The results do not establish a general winner or that these methods would behave similarly with unmeasured variants, another seed or another protein. Coverage observations do not establish future coverage.

The genetic adaptation takes the top ten previously measured parents, forms all unique single-crossover sequences and selects measured-pool candidates at most one substitution from those sequences and at most two from a parent. Intermediates are not measured or assigned ground-truth scores. The AdaLead-style adaptation uses up to ten parents within 5% of the best measured score, considers measured-pool one-step neighbors, and expands a second step only when the intermediate's prediction is at least its parent's prediction. This replaces the original algorithm's randomized proposal rollouts with an exhaustive, bounded neighborhood. Its sparse-pool stop is therefore a property of this adaptation and dataset, not a failure rate for [the original AdaLead algorithm](https://github.com/samsinai/FLEXS/blob/master/flexs/baselines/explorers/adalead.py).

An independent audit used mutation-position dictionaries rather than the implementation's distance matrix to reconstruct every parent set, proposal set and selected ordering, including the final empty neighborhood. It also checked the shared initial and range-setting examples, model seed assignments, source scores, budget and stop. Full compressed records and hashes are in [recombination output](../../../output/amylase/search/amylase_local_genetic_seed13), [AdaLead-style output](../../../output/amylase/search/amylase_local_adalead_seed13) and [the comparison summary](../../../output/amylase/search/amylase_local_comparison_seed13). All 71 backend tests passed, including rollout gating, negative-score parent thresholds, ties, invalid overlap, no-neighbor stopping and preserving the unspent budget.

Reproduce with new output directories:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend:. python3 -m scripts.amylase.run_prediction_pilot output/my-genetic --seed 13 --role-seed 2013 --member-seed 3013 --local-search genetic
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend:. python3 -m scripts.amylase.run_prediction_pilot output/my-adalead --seed 13 --role-seed 2013 --member-seed 3013 --local-search adalead
```

Further seeds, fair comparisons across all intended methods, and evaluation on the remaining proteins are still needed. These results do not validate CERA's warnings or repairs.
