# Later rollback: Amylase development check

The [protocol](later_rollback_protocol.md) compares the existing repair policy with an opt-in monitor that can restore the immediately previous reward after an accepted change if fewer than 75% of the next 30 recorded ranges cover their measurements. Both policies retain the ordinary stop after repeated failed repairs. This is a post-result-motivated development check on one measured protein, not independent biological validation.

| Seed | New measurements, both policies | Best score, both policies | Monitored outcome |
| ---: | ---: | ---: | --- |
| 161 | 100 | 0.169933 | Accepted change; only 20 later measurements available |
| 162 | 100 | 0.194283 | No accepted change |
| 163 | 100 | 0.192350 | Accepted change; 28 of 30 later ranges covered, so retained |
| 164 | 40 | 0.179917 | No accepted change; stopped after failed repairs |
| 165 | 20 | 0.201233 | No accepted change; stopped after failed repairs |

No monitored run triggered a rollback. All paired selections, final scores and measurement counts matched in this small sample. These observations do not establish equivalence or show whether restoring a previous rule would help: only one accepted change had 30 later measurements and its coverage did not trigger the rule. The other accepted change had insufficient follow-up. Synthetic tests separately exercised rollback at 22/30 coverage, retention at 23/30, supersession, invalid evidence and a complete episode with a restored rule.

The [audit](../output/amylase_later_rollback_161_165_audit.json) checked ten runs, 72 selection batches and 42 repair replays. For monitored runs it independently reconstructed the accepted-rule lineage, later coverage, decisions and insufficient-follow-up records. It found two monitoring starts, four partial updates, one retained change and one incomplete window. The audit used recorded model predictions and did not independently refit every predictor or establish that a change caused later coverage. A separate one-off comparison checked selected identifiers across all five pairs. The [per-run summary](../output/amylase_later_rollback_161_165/summary.csv) and complete compressed records preserve the actual measurements and stop reasons.

The feature is opt-in and restricted to Amylase development; the completed IRED and Hydro studies did not use it. It is an operational monitoring rule, not a validated causal safeguard or a promise of future coverage. Ordinary study evaluators reject records that enable this experimental setting.
