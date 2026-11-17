# Exploratory disagreement and measured ranking findings

The [protocol](disagreement_ranking_protocol.md) compares saved pre-reveal warnings with the ordering of measurements revealed afterward in ten previously inspected Amylase development runs. Each batch contains ten selected variants. All 100 batch correlations were defined.

| Disagreement warning | Batches | Median selected-batch rank correlation |
| --- | ---: | ---: |
| Triggered | 98 | 0.109 |
| Not triggered | 2 | 0.024 |
| Unavailable | 0 | Not defined |

A rank correlation of 1 means the two orderings agree perfectly; a value near 0 means there is little monotonic association in that batch. These are descriptive medians across dependent batches, not independent-protein results. The two unwarned batches are too few to support a dependable comparison. More fundamentally, the warning compares model rankings over 100 candidates, whereas the correlation compares the average prediction with measurements for ten selected candidates. Selection is based on predictions. These figures therefore do not establish warning accuracy, a causal effect, or performance on unselected candidates.

The [saved output](../output/amylase_disagreement_ranking.json) records the 100 batch results, seed, warning status and input and evaluator fingerprints. The evaluator checks original compressed and uncompressed hashes, replay-to-source identity, warning chronology, selected identifiers and finite data. Replay hashes are recorded rather than independently pinned; the evaluator does not recompute warning correlations or refit models. A separate one-off calculation using independently computed average ranks and Pearson correlation verified all 100 coefficients; that calculation was not saved as a reusable audit. Focused tests checked matching and opposite orders, tied and constant measurements, invalid chronology, group mismatches and non-finite values. The full backend suite passed 103 tests.

A subsequent read-only one-off calculation independently ranked the saved five-member predictions and recalculated all 100 replayed disagreement-warning correlations and statuses. All matched the records. It did not refit the predictors or independently reproduce their recorded predictions, and the check was not saved as a reusable audit.

The independent event definitions and controlled tests required for detector precision and recall remain unfinished. This report does not tune a threshold or use test-landscape outcomes.
