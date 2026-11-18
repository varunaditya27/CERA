<div align="center">

# Reactive calibration after a coverage warning

Protocol and findings

</div>

## Protocol

The current model is refitted each round, but the same 20 initially measured variants set its prediction-range width every time. A weight change alone cannot update those calibration examples. This development experiment tests a direct response to a coverage warning: use recently revealed measurements to set the next round's range, while excluding those measurements from that round's model fitting and cross-validation.

### Rule

Start with the same 100 initial measurements and the same random set of 20 reserved for range setting as the existing workflow. Continue to save every candidate's range before revealing its score. If the existing coverage warning fires and the run can continue, replace the reserved set with the 20 most recently revealed candidates, in chronological reveal order, then sort their identifiers for reproducible fitting. Apply the replacement **only from the next round onward**. At every subsequent round fit the predictor and choose its regression penalty using all revealed examples except the current 20 reserved identifiers. Compute the same 90% order-statistic range radius using those 20 reserved examples and the newly fitted model. Repeat the update after a later triggered warning, using the newest 20 revealed examples; do not remove measurements from the run or change its budget, candidate pool, reward weights, hard constraints or stop rule.

This is a pragmatic development policy, not an implementation of a proven online conformal method. Recently acquired examples are selected adaptively and their scores may have influenced earlier models and selections. Exclusion from the current fitting set prevents direct reuse in that fit, but does not restore independence or guarantee 90% future coverage. [Fannjiang et al.](https://pmc.ncbi.nlm.nih.gov/articles/PMC9618043/) describe how feedback between predictions and selected biomolecular designs changes conformal assumptions. A coverage warning or improved later coverage does not prove that the selected calibration examples caused a change.

Keep the feature opt-in and restricted to Amylase development. Do not use evaluation proteins or previously observed test outcomes to tune it. Normal study evaluators and audits must reject records that enable it. Record the trigger, old and new calibration identifiers, activation round and model-fitting identifiers so a separate audit can reconstruct the timeline and check disjoint roles.

### Checks and comparison

Use synthetic tests to check strict threshold and chronology, repeated warnings, unique and previously revealed identifiers, no direct fitting overlap, unchanged historical mode and tampering. In a complete synthetic episode, trigger a warning and verify the new set is used only in the next round. Then compare fixed-reward search with and without reactive calibration on five matched Amylase starts 171–175. Both use the existing reward, initial observations, model seeds, unrestricted eligible pool, batches and 100-measurement cap; neither changes reward weights or uses Gemini. Report warning counts, updates, range coverage and widths, actual selection counts and best scores. Mark the comparison inconclusive if warnings do not occur. Check every selection, reveal, score, role assignment and recorded update independently; save fingerprints and do not infer biological generalization or a causal guarantee from five repeated starts.

## Findings

The [protocol](reactive_calibration.md#protocol) tests an opt-in response to a coverage warning. After a warning, the next round uses the 20 most recently revealed variants to set prediction-range width and excludes them from that round's model fitting. Both comparison arms use the same fixed reward, starting observations, model seeds, unrestricted eligible pool and 100-new-measurement budget. Neither arm uses Gemini or reward repair. This is an exploratory, post-result-motivated check on one measured protein.

| Seed | Fixed calibration: covered / 100 | Reactive: covered / 100 | Fixed best score | Reactive best score | Updates |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 171 | 99 | 99 | 0.181200 | 0.181200 | 0 |
| 172 | 78 | 80 | 0.194283 | 0.180417 | 2 |
| 173 | 85 | 91 | 0.169667 | 0.169667 | 1 |
| 174 | 76 | 86 | 0.177333 | 0.177333 | 3 |
| 175 | 86 | 86 | 0.179767 | 0.179767 | 0 |

All ten runs used the full budget. Across the five starts, whole-run coverage was 424/500 with fixed calibration and 442/500 with reactive calibration. Mean range width increased from about 0.1633 to 0.1736 on this dataset's score scale. The reactive arm found a lower final best score in one pair and tied in four. These whole-run counts include observations before any update. The policies selected different batches after updates in three starts, so differences cannot be attributed solely to interval width or treated as independent observations. Five starts on the same protein do not establish general improvement or a coverage guarantee.

The [audit](../../../output/amylase_reactive_calibration_171_175_audit.json) checked ten runs, 100 selections and six updates. It reconstructed each update from the coverage-warning history, checked that new range-setting identifiers were already revealed, and verified that each round's fitting and calibration identifiers were disjoint. It also checked recorded selections and source measurements; it did not independently refit every predictor. Synthetic tests exercised the same chronology, rejected a changed update, and checked the behavior when repair is enabled or stops the run. All 158 backend tests passed.

The feature is restricted to Amylase development and is disabled by default. It can be used in an Amylase reward run with `--reactive-calibration`; it can also be combined with `--repair`, but the real comparison above tested fixed reward only. It cannot be combined with the other experimental development modes. Adaptive selection means that replacing the reserved examples does not restore the ordinary conformal assumptions or guarantee future coverage. Existing IRED and Hydro studies did not use this policy.
