# Exploratory warning follow-up findings

This applies the [follow-up protocol](warning_followup_protocol.md) to ten previously inspected Amylase development runs. It is not independent validation and does not establish accuracy for all five warning checks. A later event means fewer than 26 of the next 30 selected measurements fell inside their own previously recorded prediction ranges.

| Earlier warning | Warning and later event | Warning without later event | No warning and later event | Neither | Warning unavailable | Insufficient later measurements |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Unfamiliar candidates plus range misses | 1 | 4 | 14 | 51 | 0 | 30 |
| Low recent coverage | 0 | 4 | 11 | 35 | 20 | 30 |

Unavailable warnings take precedence in this table if follow-up is also insufficient. The two outcomes in a row can overlap with outcomes in other rows because later windows overlap; these are not independent examples. The selected variants depend on earlier measurements, and early follow-up is unavailable for coverage warnings because that check itself needs 30 measurements. The results describe these selected runs and this specific later event, not a population-level false-alarm rate or proof of the cause of a range miss. No confidence intervals or causal claim are warranted from this table.

The [machine-readable output](../output/amylase_warning_followup.json) includes input and evaluator fingerprints, all 200 opportunity rows, per-seed counts, precision and recall with undefined denominators represented as null. The evaluator verifies source compressed and content hashes, checks replay-to-source identity and selection chronology, and calculates later coverage from saved ranges and measurements. The replay files' hashes are recorded, not checked against a separately pinned manifest, and this evaluator does not independently recompute warning evidence or refit predictors. The earlier [replay audit](warning_checks_findings.md) has a different scope.

An independent one-off calculation re-read the original selections and reveals and checked all 200 later-window rows; it was not saved as a reusable audit. Four focused tests cover later-window separation, the 25/26 boundary, unavailable denominators and altered records. The complete backend suite passed 101 tests. The implementation does not modify warnings, thresholds, or the experiment runner.

A subsequent read-only one-off check matched each replay file's current hash to the hashes saved in both exploratory outputs, then recalculated all 100 support-warning statuses and all 100 coverage-warning statuses from the saved snapshots, prediction ranges and measured scores. The support check reused the recorded distances and did not regenerate them; matching recorded hashes does not itself authenticate the replay. This check was not saved as a reusable audit.

The remaining work includes separately defensible outcomes for disagreement and diversity, controlled invalid-proposal testing beyond the existing boundary tests, and independent evaluation on data not used to develop the definitions. These results do not authorize tuning against the test landscapes.
