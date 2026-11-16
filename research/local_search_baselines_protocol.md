# Finite-pool evolutionary baselines: development protocol

Recorded before implementation and runs on 16 November 2026. These are adaptations to a fixed measured pool, not exact reproductions of unrestricted genetic search or [FLEXS AdaLead](https://github.com/samsinai/FLEXS/blob/master/flexs/baselines/explorers/adalead.py). They are exploratory amylase development comparisons.

## Shared rules

Use the same seed-13 initial measurements, seed-2013 range-setting role assignment, seed-3013 model-member generator, five-predictor group, eligible pool, four-substitution limit, batches of at most ten and maximum 100 new measurements as the earlier matched greedy run. Fit and predict on the same schedule. Rank all proposed, eligible, unqueried candidates by mean predicted score, breaking ties by identifier. Never read an unqueried score or original split label when generating or ranking proposals.

For each round choose at most ten parent variants from previously measured variants, ordered by measured score and then identifier. A proposal must be at most two residue substitutions away from at least one selected parent. If fewer than ten proposals remain, measure only those; if none exist, stop with `no_neighbors` and record unspent budget. Do not silently fill a batch with distant candidates. Counts, parent IDs and proposed IDs must be saved before measurements are revealed.

## Recombination-and-mutation baseline

Use the ten highest-scoring measured parents. Generate unique single-crossover sequences by joining the prefix of one parent and suffix of another at each informative position; include the parent sequences themselves as possible recombination outputs. No score is obtained for an intermediate sequence. A measured-pool candidate is eligible for proposal if it differs by at most one substitution from one of these recombination outputs **and** at most two substitutions from a selected parent. The full eligible finite pool is scanned rather than generating and testing arbitrary unmeasured mutations. This is a deterministic, one-generation finite-pool genetic adaptation, not a standard stochastic genetic algorithm with multiple generations.

## AdaLead-style baseline

Take up to ten highest-scoring measured parents whose score is at least `best - 0.05 * abs(best)`. For each parent, propose all unqueried measured-pool variants at distance one. Continue one more mutation step from any measured-pool one-step neighbor whose model prediction is at least the parent's model prediction; add its one-step unqueried neighbors that are within two substitutions of that original parent. Previously measured sequences may act as intermediate nodes, but only unqueried candidates can be selected. This exhaustively searches a two-step finite-pool neighborhood instead of the original algorithm's randomized rollouts and recombination, and uses model predictions for continuation, so call it AdaLead-style rather than AdaLead.

## Checks and interpretation

Test mutation distance, recombination, rollout gating, deterministic ties, repeated measurements, partial batches and empty neighborhoods on hand-checkable synthetic sequences. Independently reconstruct parent choices, proposal sets and selected rankings for all rounds; check source measurements, budgets, initial data and model seeds. Evaluate the eligible-pool optimum only after both methods have stopped, and retain complete records and failures. One run on one protein cannot establish a general winner, and the finite-pool restriction can substantially change the behavior of either method.
