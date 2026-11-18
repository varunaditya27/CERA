<div align="center">

# First integrated repair pilot

Findings

</div>

Completed 16 November 2026. This development run checks the mechanics of warning-driven rule changes and stopping. It does not validate a detector, establish the cause of a warning, demonstrate recovery or show that repairs improve protein search.

## How the loop works

Before each batch, the runner saves the candidate predictions and distances, the current reward specification, the interval-setting evidence and earlier known-example features. The latter use each known representation's distance to its nearest **other** known representation. Earlier ranking predictions include examples used to fit the model, so that check is potentially optimistic. The interval-setting examples are reused; their coverage is not independent evidence of future coverage. See [Fannjiang et al. (2022)](https://pmc.ncbi.nlm.nih.gov/articles/PMC9618043/) for why adaptive selection complicates standard prediction-range guarantees.

After revealing the batch and recording all five warnings, the experimental rule-based coordinator handles triggered warnings in the order support shift, low coverage, disagreement and diversity. Constraint violations remain hard failures before reveal. For support shift, the targets are the newly revealed variants that met the joint distance-and-missed-range condition. For coverage, the targets are misses in the latest batch; a warning caused only by earlier misses has no current target and is recorded without inventing one. Disagreement and diversity are warnings rather than measured errors; for this development implementation, their targets are the just-selected batch. Requiring **every** such target to disappear from the replayed batch is a strict design choice that can make acceptance difficult.

Each candidate reward change is checked against the saved pre-reveal candidate snapshot and previously known observations. Once a change is accepted, subsequent warning handling replays the selection with the updated reward; a diversity warning is recomputed on that replay. The recorded coverage, support and predictor-disagreement observations themselves are historical evidence and are not falsely erased by a weight change. If the relevant original targets are already absent from the replay, the coordinator records that fact without counting a failed repair. An accepted change resets the consecutive-failure counter. Two failed repair attempts in a row retain the previous rule and stop the run with the remaining budget recorded. These are development semantics, not a demonstration of recovery.

The menu and verification checks are documented in [repair foundation](repair_foundation.md). The goal compiler's saved Gemini-proposed weights were used to start this run; Gemini did **not** choose the repairs. There is no model-assisted repair selection yet.

## Observed run

Seed 13 started with 100 known measurements and completed two batches of ten. The disagreement warning fired in both. In each batch all three allowed uncertainty-penalty proposals failed the requirement to displace every flagged batch member, so the original rule was retained twice. The run then stopped as `failed_repairs`, leaving **80 of 100** new measurements unused. This result highlights the interaction between the frequently triggered disagreement warning and the strict replay check; it does not demonstrate a false-alarm rate, a bad biological choice, or that another threshold would work better.

An independent audit compared both original selections with the corresponding non-repair run, reconstructed every candidate distance and every proposed batch, recalculated the recorded calibration and ranking checks, verified source measurements and chronological order, and checked the final stop and remaining budget. The compressed record, hashes, coverage table and audit are in [the pilot output](../../../output/amylase/repair/amylase_repair_pilot_seed13). The backend suite passed 50 tests, including priority, failure counting, reset after an accepted change, unchanged budget on early stop and refusal to reveal after stopping. Accepted changes were checked on controlled test data; this pilot did not accept one.

Reproduce with the pinned representations and a new output directory:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend:. python3 -m scripts.amylase.run_reward_pilot output/my-repair-pilot output/goals/gemini_goal_check/result.json --seed 13 --repair
```

The saved specification makes this replay independent of a new Gemini call. Repair behavior, priority semantics, evidence quality, thresholds and the effect of stopping require further evaluation and refinement before any final experiment.
