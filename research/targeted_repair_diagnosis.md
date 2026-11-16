# Why targeted repair runs stopped early

## Scope and method

This is a retrospective diagnosis of the five targeted amylase runs recorded in `output/amylase_targeted_disagreement_31_35/`. These runs were a development check, not an independent test. Counts below describe their saved records only. The earlier ten-seed experiment motivated a different disagreement-target rule; the present diagnosis must not be treated as a preregistered evaluation of a new rule.

## What happened

| Seed | Failed repair actions: round, warning, targets | New measurements |
| --- | --- | ---: |
| 31 | 3 coverage, 6; 4 coverage, 2 | 40 |
| 32 | 3 coverage, 3; 4 coverage, 4 | 40 |
| 33 | 3 coverage, 4; 4 coverage, 5 | 40 |
| 34 | 3 diversity, 10; 7 disagreement, 1 | 70 |
| 35 | 3 disagreement, 3; 3 diversity, 10 | 30 |

Each action tried three candidate weight changes. All 30 attempts failed `counterexamples_displaced`; all other recorded checks passed. The verifier requires every target to be absent from the batch selected by the revised reward. In the two diversity actions, all ten original batch members were targets, yet the strongest observed replay still retained nine members in seed 34 and eight in seed 35. An independent retrospective calculation from the source sequences shows that all six replayed batches met the current diversity threshold of an average of at least two sequence positions differing: seed 34 produced averages 2.0, 2.0 and 2.6; seed 35 produced approximately 2.178, 2.178 and 2.8. The other recorded verifier checks passed for all six. Under a direct diversity check they would have passed the recorded checks for those particular replays, but this does not establish what would occur in later rounds after a change is accepted.

Coverage refers to the share of measured scores falling inside the prediction ranges recorded before those measurements. Its warning examines the last 30 measurements, but its repair targets are the misses in the current batch only. The warning can therefore reflect a history wider than the targets used for the proposed repair. Across the six coverage actions in these runs, the attempted changes retained all targets except that the largest adjustment displaced one target in one action each for seeds 31 and 33. In both disagreements, no proposed weight removed any target.

The counter named `consecutive_failures` counts failed repair actions, including actions from different warning types or different rounds. A round with no attempted repair does not reset it. Two such failures stop the experiment; seed 34's failures occurred four rounds apart, and seed 35's two failures occurred in the same round. This is the behavior of the current code, not evidence that the stop policy is scientifically optimal.

## What the checks do and do not establish

The proposed changes affect selection weights, but the calibration check evaluates the already recorded prediction ranges against the same reserved examples. It does not recalculate the prediction ranges under a proposed reward change. Thus passing that check does not show that a change improves future range coverage. The earlier-ranking check uses predictions of the current model on known fitting examples; it is a guard on recorded in-sample ranking, not independent generalization evidence.

The range construction uses a reserved set and a conformal-style residual quantile. Standard conformal coverage depends on assumptions about how calibration and future examples relate; adaptively chosen candidates can differ from the calibration set, and overall coverage does not automatically guarantee coverage for a selected group. The 2021 paper [Adaptive Conformal Inference Under Distribution Shift](https://proceedings.neips.cc/paper/2021/file/0d441de75945e5acbc865406fc9a2559-Paper.pdf) explains the exchangeability assumption and why changing data distributions matter; the 2025 paper [Confidence on the focal: conformal prediction with selection-conditional coverage](https://academic.oup.com/jrsssb/article/87/4/1239/8113856) addresses coverage after selection under its own assumptions. Neither source validates this project's implementation or a particular stopping threshold.

## Design choices requiring review

1. **Keep the strict rule.** Continue only if a proposed weight change removes every flagged item. This is simple and conservative, but for a batch-level diversity warning it demands a completely different batch even when a smaller change might fix the warning. This preserves current behavior and historical comparability.
2. **Check the warning directly.** For a diversity warning, replay the proposed batch and check whether its average pairwise sequence difference reaches the existing warning threshold; for other warnings, retain their current checks until a warning-specific measure is separately defined. This aligns the diversity acceptance check with the problem it detects, but a replay is not proof that the new candidates will perform well. A new matched comparison is needed and the existing default should be preserved for comparison.
3. **Allow partial target removal.** Require a chosen fraction or number of flagged items to leave the batch. This is straightforward to measure but the cutoff needs independent justification, and removing some items may still leave a diversity warning unresolved.

Separately, the failure counter could keep its current action-by-action meaning, count failed rounds, or reset when a round produces no attempted repair. Each changes how quickly the system stops and should be evaluated separately from changes to the repair verifier. No implementation or additional experiment is implied by this retrospective diagnosis.
