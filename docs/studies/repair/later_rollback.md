<div align="center">

# Later rollback after an accepted repair

Protocol and findings

</div>

## Protocol

The ordinary repair loop retains the old rule immediately when a proposal fails its checks. This development feature addresses a separate case: a proposal was accepted, then later predictions performed poorly. It is opt-in and restricted to Amylase repair runs while its behavior is tested. Existing matched studies and their historical records do not enable it.

After each accepted reward change, save the immediately previous and new validated specifications. Starting with the next batch, check the first 30 newly revealed measurements against the ranges recorded before their reveal. Once 30 are available, restore the immediately previous specification if fewer than 75% of those measurements were covered; otherwise retain the accepted specification. This uses the existing coverage-warning threshold and the user's approved 30-later-measurement window. Exactly 22 of 30 is below the threshold; 23 is not. A higher or lower covered count describes range coverage, not a causal estimate of the reward change's effect.

If another repair is accepted before the window finishes, mark the older observation window superseded, save the immediately preceding specification, and restart the 30-measurement window. The reward rule may already include earlier accepted changes: restoration is one step, not a reset to the original rule. A rollback does not erase measurements, alter mutation limits, change the budget or claim that the restored rule is accurate. Skip further repair attempts in the batch where rollback is applied, so warnings generated under the old selection are not immediately used to undo the rollback. Keep the existing consecutive-failure counter unchanged. Record every start, progress update, supersession, keep, rollback and incomplete window with specifications and counts.

The search may stop before 30 later measurements; record the pending check as unavailable rather than calling it successful or unsuccessful. This coverage check can reflect selection, predictor retraining, changing data or noise; it cannot establish that the accepted repair caused the later outcome. Ordinary split-conformal guarantees require conditions that can fail when data change or are adaptively selected ([Zaffran et al.](https://proceedings.mlr.press/v162/zaffran22a.html)). The threshold is a development monitoring choice, not a statistically validated intervention or a guarantee.

Tests must cover both sides of the 22/23 boundary, no early decision, superseded changes, insufficient follow-up, rollback to the correct prior version, invalid data, immutable saved specifications, and an end-to-end synthetic episode with chronological records and unchanged hard constraints. Normal matched-study evaluators and audits must reject records with the experimental mode enabled. Do not use Hydro or IRED results to tune this setting. Compare enabled and disabled policies on development data before making claims about usefulness.

### Matched development check

Compare the ordinary repair policy and the monitored policy on five matched Amylase starts 161–165, with identical starting measurements, model seeds, settings, candidate pools and a maximum of 100 new measurements. Both retain the normal stop after repeated failed repairs. The monitored policy can differ because it restores a previous rule and skips further repair actions in the rollback batch. Report accepted changes, completed monitoring windows, rollbacks, incomplete or superseded windows, actual measurement counts and best observed scores. Do not manufacture a result if no accepted repair reaches a complete window. This is an exploratory check prompted by earlier findings and uses no Gemini calls.

## Findings

The [protocol](later_rollback.md#protocol) compares the existing repair policy with an opt-in monitor that can restore the immediately previous reward after an accepted change if fewer than 75% of the next 30 recorded ranges cover their measurements. Both policies retain the ordinary stop after repeated failed repairs. This is a post-result-motivated development check on one measured protein, not independent biological validation.

| Seed | New measurements, both policies | Best score, both policies | Monitored outcome |
| ---: | ---: | ---: | --- |
| 161 | 100 | 0.169933 | Accepted change; only 20 later measurements available |
| 162 | 100 | 0.194283 | No accepted change |
| 163 | 100 | 0.192350 | Accepted change; 28 of 30 later ranges covered, so retained |
| 164 | 40 | 0.179917 | No accepted change; stopped after failed repairs |
| 165 | 20 | 0.201233 | No accepted change; stopped after failed repairs |

No monitored run triggered a rollback. All paired selections, final scores and measurement counts matched in this small sample. These observations do not establish equivalence or show whether restoring a previous rule would help: only one accepted change had 30 later measurements and its coverage did not trigger the rule. The other accepted change had insufficient follow-up. Synthetic tests separately exercised rollback at 22/30 coverage, retention at 23/30, supersession, invalid evidence and a complete episode with a restored rule.

The [audit](../../../output/amylase/repair/amylase_later_rollback_161_165_audit.json) checked ten runs, 72 selection batches and 42 repair replays. For monitored runs it independently reconstructed the accepted-rule lineage, later coverage, decisions and insufficient-follow-up records. It found two monitoring starts, four partial updates, one retained change and one incomplete window. The audit used recorded model predictions and did not independently refit every predictor or establish that a change caused later coverage. A separate one-off comparison checked selected identifiers across all five pairs. The [per-run summary](../../../output/amylase/repair/amylase_later_rollback_161_165/summary.csv) and complete compressed records preserve the actual measurements and stop reasons.

The feature is opt-in and restricted to Amylase development; the completed IRED and Hydro studies did not use it. It is an operational monitoring rule, not a validated causal safeguard or a promise of future coverage. Ordinary study evaluators reject records that enable this experimental setting.
