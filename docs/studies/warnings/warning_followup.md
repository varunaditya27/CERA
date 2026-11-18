<div align="center">

# Exploratory warning follow-up protocol

Protocol and findings

</div>

## Protocol

Approved implementation direction: evaluate what the existing Amylase development records can support, without claiming that all five warning types have been scientifically validated. These records have already informed development; this is an exploratory retrospective analysis, not a held-out validation. The original warning implementations and thresholds remain unchanged.

For each recorded support-shift or low-coverage warning at the end of a batch, examine the next 30 *new* measurements in that same run. The outcome is whether fewer than 26 of those 30 measurements fell inside their own prediction ranges saved before their measurement. This 85% boundary is the lower edge of the previously approved 90% ± 5 percentage-point recovery band; this analysis asks a different question from recovery and does not assert that a warning or repair caused the later result. Calculate coverage independently from each later selection and reveal, not from the later coverage warning. The current batch is excluded. The outcome is observed later coverage, not the unknown long-run probability of coverage.

Count each warning opportunity, its status, and whether 30 subsequent measurements exist. Report missing follow-up and unavailable warnings separately. For cases with both available, report the four counts: triggered with and without the later event, and not triggered with and without it. Report precision and recall only when their denominators are nonzero. Include seed-level counts: consecutive windows overlap and are not independent experiments, so pooled counts are descriptive and must not be treated as independent replicates. This 30-measurement follow-up does not guarantee detection of a persistent fault; finite samples and adaptive selection affect the outcome.

The historical source manifest must match both compressed and uncompressed record hashes, and the replay must name the matching compressed hash. Check record chronology, selected and revealed identifiers, finite saved bounds and measurements, and warning round/status alignment before calculating. Record hashes of the replay inputs and evaluator source in the result. Prior replay auditing provides additional context, but the new evaluator cannot establish all source or replay claims merely by reading these hashes. A mismatch or malformed record is an error, not a negative outcome.

The constraint and diversity checks have existing unit tests against stated rules; those are correctness checks, not evidence of a biological outcome. Ranking disagreement does not directly assert future range failure, so this protocol does not present that outcome as its ground truth. Independently defined ranking errors, injected conditions for all five types, and independent test evaluation remain open. Do not use these exploratory results to choose test-data thresholds.

Research context: [Fannjiang et al. (2022)](https://pmc.ncbi.nlm.nih.gov/articles/PMC9618043/) describe dependence induced by model-directed biomolecular design; their coverage guarantees do not automatically apply to these intervals. The [scikit-learn precision and recall documentation](https://scikit-learn.org/stable/auto_examples/model_selection/plot_precision_recall.html) defines the corresponding classification counts. A later observed outcome helps avoid using the same observations for both warning and outcome; it is not, by itself, external validation or evidence of causality.

## Findings

This applies the [follow-up protocol](warning_followup.md#protocol) to ten previously inspected Amylase development runs. It is not independent validation and does not establish accuracy for all five warning checks. A later event means fewer than 26 of the next 30 selected measurements fell inside their own previously recorded prediction ranges.

| Earlier warning | Warning and later event | Warning without later event | No warning and later event | Neither | Warning unavailable | Insufficient later measurements |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Unfamiliar candidates plus range misses | 1 | 4 | 14 | 51 | 0 | 30 |
| Low recent coverage | 0 | 4 | 11 | 35 | 20 | 30 |

Unavailable warnings take precedence in this table if follow-up is also insufficient. The two outcomes in a row can overlap with outcomes in other rows because later windows overlap; these are not independent examples. The selected variants depend on earlier measurements, and early follow-up is unavailable for coverage warnings because that check itself needs 30 measurements. The results describe these selected runs and this specific later event, not a population-level false-alarm rate or proof of the cause of a range miss. No confidence intervals or causal claim are warranted from this table.

The [machine-readable output](../../../output/amylase_warning_followup.json) includes input and evaluator fingerprints, all 200 opportunity rows, per-seed counts, precision and recall with undefined denominators represented as null. The evaluator verifies source compressed and content hashes, checks replay-to-source identity and selection chronology, and calculates later coverage from saved ranges and measurements. The replay files' hashes are recorded, not checked against a separately pinned manifest, and this evaluator does not independently recompute warning evidence or refit predictors. The earlier [replay audit](warning_checks.md#findings) has a different scope.

An independent one-off calculation re-read the original selections and reveals and checked all 200 later-window rows; it was not saved as a reusable audit. Four focused tests cover later-window separation, the 25/26 boundary, unavailable denominators and altered records. The complete backend suite passed 101 tests. The implementation does not modify warnings, thresholds, or the experiment runner.

A subsequent read-only one-off check matched each replay file's current hash to the hashes saved in both exploratory outputs, then recalculated all 100 support-warning statuses and all 100 coverage-warning statuses from the saved snapshots, prediction ranges and measured scores. The support check reused the recorded distances and did not regenerate them; matching recorded hashes does not itself authenticate the replay. This check was not saved as a reusable audit.

The remaining work includes separately defensible outcomes for disagreement and diversity, controlled invalid-proposal testing beyond the existing boundary tests, and independent evaluation on data not used to develop the definitions. These results do not authorize tuning against the test landscapes.
