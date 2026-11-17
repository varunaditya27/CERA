# Reactive calibration: Amylase development check

The [protocol](reactive_calibration_protocol.md) tests an opt-in response to a coverage warning. After a warning, the next round uses the 20 most recently revealed variants to set prediction-range width and excludes them from that round's model fitting. Both comparison arms use the same fixed reward, starting observations, model seeds, unrestricted eligible pool and 100-new-measurement budget. Neither arm uses Gemini or reward repair. This is an exploratory, post-result-motivated check on one measured protein.

| Seed | Fixed calibration: covered / 100 | Reactive: covered / 100 | Fixed best score | Reactive best score | Updates |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 171 | 99 | 99 | 0.181200 | 0.181200 | 0 |
| 172 | 78 | 80 | 0.194283 | 0.180417 | 2 |
| 173 | 85 | 91 | 0.169667 | 0.169667 | 1 |
| 174 | 76 | 86 | 0.177333 | 0.177333 | 3 |
| 175 | 86 | 86 | 0.179767 | 0.179767 | 0 |

All ten runs used the full budget. Across the five starts, whole-run coverage was 424/500 with fixed calibration and 442/500 with reactive calibration. Mean range width increased from about 0.1633 to 0.1736 on this dataset's score scale. The reactive arm found a lower final best score in one pair and tied in four. These whole-run counts include observations before any update. The policies selected different batches after updates in three starts, so differences cannot be attributed solely to interval width or treated as independent observations. Five starts on the same protein do not establish general improvement or a coverage guarantee.

The [audit](../output/amylase_reactive_calibration_171_175_audit.json) checked ten runs, 100 selections and six updates. It reconstructed each update from the coverage-warning history, checked that new range-setting identifiers were already revealed, and verified that each round's fitting and calibration identifiers were disjoint. It also checked recorded selections and source measurements; it did not independently refit every predictor. Synthetic tests exercised the same chronology, rejected a changed update, and checked the behavior when repair is enabled or stops the run. All 158 backend tests passed.

The feature is restricted to Amylase development and is disabled by default. It can be used in an Amylase reward run with `--reactive-calibration`; it can also be combined with `--repair`, but the real comparison above tested fixed reward only. It cannot be combined with the other experimental development modes. Adaptive selection means that replacing the reserved examples does not restore the ordinary conformal assumptions or guarantee future coverage. Existing IRED and Hydro studies did not use this policy.
