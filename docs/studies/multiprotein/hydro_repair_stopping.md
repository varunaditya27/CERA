<div align="center">

# Hydro repair-stopping diagnosis protocol

Protocol and findings

</div>

## Protocol

The [completed Hydro study](hydro_low_fitness.md#findings) stopped 27 of 30 runs in each repair arm after repeated failed repair actions. This post-result diagnosis examines the saved actions; it does not change a policy or make a new biological experiment. Its purpose is to identify the observed mechanism before designing further Amylase-only development tests. The Hydro starting pool was selected using measured fitness, and its test outcomes must not be used to tune the policy.

For both repair arms on all 30 matched starts, read the fingerprint-verified compressed records. Separately count warning-triggered action statuses, attempted and rejected proposals, the checks that were false or unavailable, and actions with no proposals. One rejected proposal can fail more than one check, so overlapping reason counts must not be added as though they were distinct proposals. Report checks by warning type and arm. For each early stop, reconstruct the consecutive failed-action counter, identify the two final failed actions and state whether they occurred in the same batch or different batches. A successful action resets the counter; warnings that do not cause an attempted repair do not increment it. Verify the terminal status and counter chronology instead of assuming the stop happened after two batches.

For calibration checks, record the calibration count and pass/fail as saved; changing a reward weight does not itself refit the predictor or change the recorded intervals in that replay. This check can preserve an existing calibration property but cannot alone demonstrate correction of later coverage. The current verifier's displacement check requires every named counterexample to be absent from the replayed batch; a failed check describes that operational requirement, not proof that the alternative candidates would be better.

Check that all 60 expected runs and each compressed and uncompressed fingerprint are present. Save the source-record fingerprints and exact per-run counters, aggregate per protein and arm, and reject unknown action statuses or inconsistent failure counters. Unit tests cover multiple failed checks, an accepted reset, failures in the same versus different batches, no-op warnings, missing attempts and tampered counters. Independently compare the recorded attempt counts against the previously audited study report. Use the existing data only descriptively; these are repeated starts on three fixed protein groups, not independent biological replications.

Selective prediction involves a tradeoff between declining to act and acting with potential error, but the general [selective prediction literature](https://academic.oup.com/biometrics/article/79/2/811/7513980) does not prove that CERA's stopping rule is safe or optimal. Standard coverage assumptions may fail under changing or dependent data, as described by [Retzlaff et al.](https://proceedings.mlr.press/v266/retzlaff25a.html); observed interval misses and check failures must not be presented as a formal guarantee.

## Findings

The [diagnosis](../../../output/multiprotein/hydro/hydro_repair_stopping_diagnosis.json) reads the 60 saved repair-policy runs in the exploratory Hydro low-fitness-start study. It describes recorded checks after the results were known. It does not establish what would have happened had the search continued, or establish that any rejected repair would have helped.

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

The [separate audit](../../../output/multiprotein/hydro/hydro_repair_stopping_diagnosis_audit.json) checked 60 fingerprint-verified records and 363 proposals, reconstructed per-run check counts and final failed actions, and verified key aggregates. The earlier [decision audit](../../../output/multiprotein/hydro/hydro_low_fitness_141_150_audit.json) reconstructed selections and repair replays. These checks reuse recorded predictions and do not independently refit every predictor or validate biological causes. All 146 backend tests passed after the diagnostic implementation.
