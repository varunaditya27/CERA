# Amylase warning-check development findings

Implemented and checked 16 November 2026 under the [warning design](warning_checks_design.md). These warning rules are development thresholds, not validated diagnoses, error rates or evidence that a repair would work. The retrospective replay and fresh pilot are not final evaluations.

## What was implemented

The five checks cover invalid requests, unfamiliar candidates that also miss a prediction range, low observed range coverage, disagreement among individual predictor rankings, and low sequence diversity within a batch. Each emits `triggered`, `not_triggered`, or `unavailable`. Invalid inputs raise errors. Existing measurement-runner checks still reject invalid batches without revealing any scores or spending budget.

For new runs, individual member predictions for the top candidates and the nearest-known-distance snapshot are recorded before scores are revealed. Support and rolling-coverage checks are recorded afterward. The distance threshold uses raw Euclidean distance to the nearest *other* known representation, with the 90th percentile defined in the design; this remains a provisional clarification of the synopsis's normalized-distance wording, not a validated threshold.

The separate historical replay reads the ten previously saved range-pilot records, verifies their compressed and uncompressed fingerprints, checks their original source fingerprints against Git commit `78fce61`, and rebuilds the historical predictor group before computing warnings. It verifies the reconstructed top predictions and range-setting radius against each historical record. Original records are never modified; a replay log refers back to its input record and records pre- and post-reveal evidence in chronological order. Full original Git history including that commit is needed for this replay.

## Retrospective replay results

Across the ten previous runs and 100 batches:

| Warning | Triggered | Not triggered | Unavailable |
| --- | ---: | ---: | ---: |
| Constraint | 0 | 100 | 0 |
| Unfamiliar candidate plus range miss | 6 | 94 | 0 |
| Low range coverage | 7 | 73 | 20 |
| Member ranking disagreement | 98 | 2 | 0 |
| Low batch diversity | 0 | 100 | 0 |

Coverage is unavailable in the first two batches of each run because 30 newly revealed scores are required. The seven low-coverage results match the earlier post-hoc inspection. These are counts of overlapping batches from ten runs on one dataset, not precision, recall, false-alarm rate or independent biological replication. In particular, no actual constraint violation is expected when the hard filter rejects invalid requests first.

The 98 disagreement warnings make the current threshold worth investigating. In a **post-hoc** first-round analysis of the same ten reconstructed models, mean pairwise ranking correlation averaged about 0.737 across the full candidate pools and about 0.265 among only each round's top 100 candidates. The two calculations concern different candidate groups, and top candidates are selected by the same models. This shows that the warning depends strongly on the evaluation group; it does not prove why or whether a warning is useful. Per-seed values are in [first_round_rank_context.csv](../output/amylase_warning_replay_v2/first_round_rank_context.csv).

The final replay evidence and per-seed warning counts are in [amylase_warning_replay_v2](../output/amylase_warning_replay_v2). The preceding working replay was independently audited before the final replay added stricter input and source checks; the ten final warning evidence files were checked to match that audit, aside from replay metadata.

## Fresh run and verification

One fresh seed-12 pilot recorded 10 batches and pre-reveal warning evidence. Ranking disagreement triggered in all ten batches. Constraint, diversity and unfamiliar-candidate-plus-miss warnings did not trigger. The coverage warning was unavailable for the first two batches and did not trigger in the remaining eight. The pilot's saved ranges covered 99 of its 100 selected scores. These observations are one development run, not evidence of a warning's false-alarm rate.

An independent audit of the fresh record checked event order, source fingerprints, selected identities and scores, budget, mutation limits, coverage history, Hamming diversity, ranking correlation calculated independently from saved member predictions, and distances recalculated from the saved pre-reveal known sets. The same independent calculations were checked on all 100 historical replay batches. The live coverage table was reconstructed from the run record even with warning events present.

Unit tests cover positive and negative examples, strict boundaries, duplicates, invalid data, unavailable cases, ranking ties, zero-distance representations, atomic invalid-batch rejection and reconstruction of a post-reveal warning from saved pre-reveal evidence. No model thresholds were tuned as a result of the replay.

## Limitations

No independently defined ground-truth dataset of warning events has been established, so precision and recall have not been measured. Correlations can be undefined for constant rankings; such cases are reported unavailable. Recorded warnings are not inferred causes and are not repairs. The current predictor group contains five ridge models, not the complete predictor mixture proposed in the synopsis. Neither warning priorities, repair selection, language-model involvement nor recovery after a repair is implemented.
