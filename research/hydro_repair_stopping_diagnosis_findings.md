# Why the Hydro repair runs stopped

The [diagnosis](../output/hydro_repair_stopping_diagnosis.json) reads the 60 saved repair-policy runs in the exploratory Hydro low-fitness-start study. It describes recorded checks after the results were known. It does not establish what would have happened had the search continued, or establish that any rejected repair would have helped.

Across all three proteins, each repair policy stopped after repeated failed repair actions in 27 of 30 starts. In all 54 such stops across both policies, the final two failed actions occurred in **different batches**. This is specific to these runs: the implementation can count more than one failed action from a single batch. Three runs per policy used the full budget.

| Recorded attempts | Rule-based repair | Gemini-assisted repair |
| --- | ---: | ---: |
| Proposed rule changes checked | 182 | 181 |
| Accepted | 3 | 3 |
| Rejected | 179 | 178 |
| Failed complete counterexample displacement | 173 | 172 |
| Failed direct diversity resolution | 6 | 6 |

Each rejected proposal failed at least one of the last two checks. Three proposals in each arm also failed the earlier-ranking preservation check, so check-failure counts can overlap. No attempted change failed the recorded calibration-coverage check, and no failed action had an empty proposal menu. Per-protein counts, warning types, batch numbers and individual records are in the diagnosis file.

Complete displacement means that **every** flagged variant must disappear when the earlier batch is replayed under the proposed rule. This is an implementation criterion, not independent evidence that replacement variants would perform better. Likewise, the calibration check uses the already recorded prediction ranges; changing a reward weight by itself does not recalculate those ranges. Passing that check therefore cannot establish that the change will improve coverage on later measurements. Neither observation proves that removing a safeguard is safe or useful.

The [separate audit](../output/hydro_repair_stopping_diagnosis_audit.json) checked 60 fingerprint-verified records and 363 proposals, reconstructed per-run check counts and final failed actions, and verified key aggregates. The earlier [decision audit](../output/hydro_low_fitness_141_150_audit.json) reconstructed selections and repair replays. These checks reuse recorded predictions and do not independently refit every predictor or validate biological causes. All 146 backend tests passed after the diagnostic implementation.
