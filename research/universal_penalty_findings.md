# Development comparison: one repair penalty

The [protocol](universal_penalty_protocol.md) compared the normal warning-specific repair mapping with an Amylase-only policy that proposes the uncertainty penalty for every warning while retaining the original warning-specific evidence checks. Five matched starts and both policies completed. This comparison was chosen after earlier outcomes had been inspected, uses one development protein and made no provider calls.

The comparison did **not exercise a difference in proposed repair term**. In each policy, the only repair actions that reached an attempt were four coverage actions and two disagreement actions; both warning types already map to the uncertainty penalty under the normal policy. No repair was accepted. All selected batches, stopping reasons, final best scores and measurement counts were identical within each pair. This is an inconclusive test of a universal penalty, not evidence that a universal penalty and type-specific repairs are equivalent.

| Seed | New measurements per policy | Best score per policy | Stop |
| ---: | ---: | ---: | --- |
| 101 | 100 | 0.170183 | Budget exhausted |
| 102 | 100 | 0.179767 | Budget exhausted |
| 103 | 40 | 0.199933 | Failed repairs |
| 104 | 100 | 0.176100 | Budget exhausted |
| 105 | 40 | 0.182250 | Failed repairs |

The [summary](../output/amylase_universal_101_105/summary.csv) preserves per-run range coverage, widths and action counts. The [independent audit output](../output/amylase_universal_101_105_audit.json) was captured directly from the completed audit: it checked ten runs, 76 selections and 36 repair replays, including matched starts, menu terms and costs, warning-specific checks, action order and stops. A separate one-off check compared selection identifiers in all five pairs; it was not saved as a reusable audit. The audit used saved predictions and distances rather than refitting every predictor.

The audit script SHA-256 was `efe33f03b560495f463c100c8b59c6b7825508c32371015fd0399dac8e4a871c`; it used `audit_development_repairs.py` SHA-256 `0774cd75ee9a53224b2b820b1c253f14b585b2bcab959fa3523145b4d43deaf5` and `audit_matched_proteins.py` SHA-256 `1a72b4a0ddcacd9194e3961c46d5746c05f5224001fca286f9ee234583c7315f`. The study manifest SHA-256 was `86f5c92070cf247c5d374bdbf7cb8b358633c7ac1093a8d873bbcaad0d2c2c70`. All 124 backend tests passed before the runs.
