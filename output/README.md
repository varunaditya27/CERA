<div align="center">

# Saved results

Generated records and reports. Treat as read-only evidence.

</div>

Each folder or file below was written by a script under `scripts/` and is described by the linked document. Run records (`.jsonl`, `.jsonl.gz`) store fingerprints of the data, caches and code that produced them. Audit scripts check those fingerprints, so records are never edited or renamed. Records written before the repository reorganisation are verified from the git tag `pre-restructure`; see [reproducing results](../docs/overview/reproducing_results.md).

| Names starting with | What they hold | Document |
| --- | --- | --- |
| `matched_eval_51_60` | Four-protein comparison, 360 runs, its audits and paired analyses | [Four-protein findings](../docs/studies/multiprotein/four_protein_findings.md) |
| `ired_low_change_61_70` | IRED low-change start study | [IRED low-change start](../docs/studies/multiprotein/ired_low_change.md) |
| `hydro_low_fitness_*` | Hydro low-fitness start study | [Hydro low-fitness start](../docs/studies/multiprotein/hydro_low_fitness.md) |
| `hydro_repair_stopping_diagnosis*` | Why Hydro repair runs stopped | [Hydro repair stopping](../docs/studies/multiprotein/hydro_repair_stopping.md) |
| `amylase_comparison`, `amylase_repeated*`, `amylase_range*`, `amylase_ranges_repeated`, `amylase_warning_*` | Early Amylase comparisons, prediction ranges and warning checks | [Amylase studies](../docs/studies/amylase/) |
| `amylase_reward_pilot`, `amylase_matched_reward`, `amylase_acquisition_*`, `amylase_local_*` | Reward pilot, matched reward comparison and search baselines | [Amylase studies](../docs/studies/amylase/) |
| `amylase_repair_pilot`, `amylase_gemini_*`, `amylase_abstention*`, `amylase_repair_terms*`, `amylase_retention*`, `amylase_universal*`, `amylase_verifier*`, `amylase_reactive_calibration*`, `amylase_later_rollback*`, `amylase_targeted_disagreement*`, `amylase_direct_diversity*` | Repair pilots and ablations | [Repair studies](../docs/studies/repair/) |
| `coverage_warning_*`, `disagreement_warning_*`, `support_warning_*`, `rule_warning_controls*`, `amylase_disagreement_*` | Controlled warning simulations and ranking checks | [Warning studies](../docs/studies/warnings/) |
| `amylase_hybrid_*`, `mixed_*`, `heldout_shift_*`, `amylase_position_*` | Mixed predictor, held-out prediction and position-shift checks | [Hybrid studies](../docs/studies/hybrid/) |
| `natural_goal_*`, `gemini_goal_check` | Gemini goal compilation checks | [Goal compiler](../docs/workspace/goal_compiler.md) |
| `representations/` | Score-free ESM-2 sequence vector caches | [ESM feasibility](../docs/background/esm_feasibility.md) |
| `web_runs/`, `web_goals/` | Created by the local web workspace when you use it | [Experiment walkthrough](../docs/workspace/experiment_walkthrough.md) |
