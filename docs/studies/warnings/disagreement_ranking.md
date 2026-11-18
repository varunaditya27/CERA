<div align="center">

# Exploratory disagreement and measured ranking

Protocol and findings

</div>

## Protocol

The original proposal requests the Spearman correlation between predicted and measured scores in each queried batch. This analysis compares that descriptive measure with the saved pre-reveal disagreement warning in the ten historical Amylase development runs (seeds 2–11). These runs were already inspected during development: this is exploratory, not independent validation.

For each batch, use the saved mean predictions and subsequently revealed experimental scores for its selected identifiers. Spearman correlation compares their order, assigning average ranks to ties. Report the coefficient rather than choosing a new cutoff and calling it a biological failure. If fewer than two selected values or either series is constant, the coefficient is unavailable. No p-values are calculated for individual small batches. The [SciPy documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.spearmanr.html) describes ties, constant inputs and small-sample caveats.

The warning measures agreement among five models over the top 100 candidates; the outcome measures the relationship between mean prediction and measurement among the selected batch, normally ten candidates. These are different groups and quantities. A warning is recorded before this batch's scores are revealed. For the historical greedy runs verify that selected identifiers belong to the warning group. Only selected candidates are examined, and they were chosen using their predictions. This selection restricts interpretation: the coefficient is not the warning's precision, recall, causal effect, or performance over the whole candidate pool. See also [Kilbertus et al. (2020)](https://proceedings.mlr.press/v108/kilbertus20a.html) on outcomes observed conditional on earlier decisions, a general illustration rather than a direct analysis of these protein records.

Check the original compressed and uncompressed fingerprints, replay-to-source compressed hash, warning and reveal chronology, selected identifiers, finite values and complete rounds. Record input and implementation hashes. Report every batch and per-warning-status sample sizes and medians, including unavailable values, alongside per-seed results. The historical replay was audited separately; this analysis does not refit models or independently prove the warning calculation. Since only two historical batches lacked a warning, comparisons between warning groups are particularly weak and should not guide threshold tuning.

## Findings

The [protocol](disagreement_ranking.md#protocol) compares saved pre-reveal warnings with the ordering of measurements revealed afterward in ten previously inspected Amylase development runs. Each batch contains ten selected variants. All 100 batch correlations were defined.

| Disagreement warning | Batches | Median selected-batch rank correlation |
| --- | ---: | ---: |
| Triggered | 98 | 0.109 |
| Not triggered | 2 | 0.024 |
| Unavailable | 0 | Not defined |

A rank correlation of 1 means the two orderings agree perfectly; a value near 0 means there is little monotonic association in that batch. These are descriptive medians across dependent batches, not independent-protein results. The two unwarned batches are too few to support a dependable comparison. More fundamentally, the warning compares model rankings over 100 candidates, whereas the correlation compares the average prediction with measurements for ten selected candidates. Selection is based on predictions. These figures therefore do not establish warning accuracy, a causal effect, or performance on unselected candidates.

The [saved output](../../../output/amylase/warnings/amylase_disagreement_ranking.json) records the 100 batch results, seed, warning status and input and evaluator fingerprints. The evaluator checks original compressed and uncompressed hashes, replay-to-source identity, warning chronology, selected identifiers and finite data. Replay hashes are recorded rather than independently pinned; the evaluator does not recompute warning correlations or refit models. A separate one-off calculation using independently computed average ranks and Pearson correlation verified all 100 coefficients; that calculation was not saved as a reusable audit. Focused tests checked matching and opposite orders, tied and constant measurements, invalid chronology, group mismatches and non-finite values. The full backend suite passed 103 tests.

A subsequent read-only one-off calculation independently ranked the saved five-member predictions and recalculated all 100 replayed disagreement-warning correlations and statuses. All matched the records. It did not refit the predictors or independently reproduce their recorded predictions, and the check was not saved as a reusable audit.

The independent event definitions and controlled tests required for detector precision and recall remain unfinished. This report does not tune a threshold or use test-landscape outcomes.
