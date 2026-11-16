# Targeted disagreement repair: development protocol

Recorded before implementing or running this development variant. The previous ten-seed observations motivated the change, so later analysis on those records would be retrospective, not independent confirmation. The existing default and historical results remain available.

## Problem observed

The current warning compares model rankings within the 100 candidates with the largest **mean predictions**, while the fixed reward also penalizes model spread and distance. In the 20 batches from the ten rule-based repair runs, only 6 of 200 selected variants were in that top-100 mean-prediction group. Nonetheless, the old repair code treated every selected variant as a disagreement target. A group-level association does not establish that an individual candidate is contested or that its prediction is wrong. Of those 200 selections, 58 missed their recorded prediction ranges; four were both misses and members of the warning's top-100 group. These are post-hoc counts from the earlier development runs, not estimates of a detector's accuracy.

## Proposed variant

Keep the existing pairwise Spearman warning threshold and its unavailable cases. When a reward is in use, construct its warning group from the top 100 candidates by the reward before the first batch choice: mean minus the current weighted spread and distance penalties. The diversity term is zero before the first choice. Break ties by identifier. This group is more closely aligned with the selector, although later diversity-aware choices can still fall outside it.

Within that group, rank each member's predicted fitness separately, assigning average ranks for ties as described in [SciPy's rank documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.rankdata.html). For a selected candidate with all five member predictions, calculate `(largest member rank - smallest member rank) / (group size - 1)`. Mark it as a disagreement target if that fraction is at least 0.5. This means members place the candidate at least half the group's rank range apart; it is a simple, interpretable **development threshold**, not a statistically validated error detector. It is not derived from the observed target counts above.

If the group has fewer than two candidates, the warning is unavailable, the warning does not trigger, or a selected item lies outside the group, do not invent a target for that item. Record which selected IDs were assessed, their rank spreads, unassessed IDs and the threshold before revealing their scores. If no target remains, retain the warning and record that no repair target is available; do not count that as a failed repair. A target indicates disagreement in rankings, not a proven error, and no outcome label is used to create it.

## Predeclared checks

- Add the change as an explicit opt-in so historical and default behavior are preserved. Test identical and opposite rankings, ties, exact threshold, below threshold, selected items outside the group, constant members, insufficient data, and malformed evidence. Preserve constraint and budget enforcement.
- Run matched amylase seeds 31–35 using the same initial measurements, example reward, role seeds `2000 + seed`, member seeds `3000 + seed` and maximum budget for a fixed-reward run and the targeted rule-based repair variant. The earlier seeds remain separate. No IRED or Hydro outcome is used for tuning. Record no-target warnings, attempted and accepted changes, stop reasons and actual query counts.
- Independently check reward group construction, pre-reveal chronology, individual rank spreads and target IDs, all selected measurements and budget accounting, and representative repair replays. Compare best observed scores and range coverage with actual denominators, without treating five seeds on one protein as independent biological replication.

The design is intended to make the warning's evidence and the repair targets refer to overlapping candidates. It does not validate the 0.5 cutoff, the warning threshold, the repair verifier or any claimed improvement. After this development check, an independently defined failure target and separate evaluation remain necessary.
