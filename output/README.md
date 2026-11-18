<div align="center">

# Saved results

Generated records and reports. Treat as read-only evidence.

</div>

Each folder or file below was written by a script under `scripts/` and is described by the linked document. Run records (`.jsonl`, `.jsonl.gz`) store fingerprints of the data, caches and code that produced them. Audit scripts check those fingerprints, so files inside a result folder are never edited or renamed. The folders themselves were grouped by topic after the studies ran. Audits that check recorded source fingerprints must be run from the git tag `pre-restructure`; see [reproducing results](../docs/overview/reproducing_results.md).

| Folder | What it holds | Document |
| --- | --- | --- |
| `multiprotein/four_protein/` | Four-protein comparison, 360 runs, its audits and paired analyses | [Four-protein findings](../docs/studies/multiprotein/four_protein_findings.md) |
| `multiprotein/ired_low_change/` | IRED low-change start study | [IRED low-change start](../docs/studies/multiprotein/ired_low_change.md) |
| `multiprotein/hydro/` | Hydro low-fitness start study and repair-stopping diagnosis | [Hydro low-fitness start](../docs/studies/multiprotein/hydro_low_fitness.md) |
| `amylase/search/` | Early Amylase comparisons, prediction ranges, reward pilot and search baselines | [Amylase studies](../docs/studies/amylase/) |
| `amylase/repair/` | Repair pilots and ablations | [Repair studies](../docs/studies/repair/) |
| `amylase/warnings/` | Warning replay and disagreement ranking | [Warning studies](../docs/studies/warnings/) |
| `amylase/hybrid/` | Mixed-predictor GPU pilots and exported model | [Mixed predictor](../docs/studies/hybrid/) |
| `warnings/` | Controlled warning simulations | [Controlled simulations](../docs/studies/warnings/controlled_simulations.md) |
| `hybrid/` | Mixed-predictor held-out and search comparisons | [Mixed predictor](../docs/studies/hybrid/) |
| `heldout/` | Held-out shift prediction and position-shift checks | [Held-out prediction](../docs/studies/hybrid/heldout_shift_prediction.md) |
| `data/` | Dataset provenance checks, such as how the IRED split was selected from the laboratory table | [IRED preparation](../docs/data/ired_preparation.md) |
| `goals/` | Gemini goal compilation checks | [Goal compiler](../docs/workspace/goal_compiler.md) |
| `representations/` | Score-free ESM-2 sequence vector caches | [ESM feasibility](../docs/background/esm_feasibility.md) |
| `packages/` | The submission review archive built by `scripts/reporting/package_submission_review.py` | [Submission readiness](../docs/overview/submission_readiness.md) |
| `web_runs/`, `web_goals/` | Created by the local web workspace when you use it | [Experiment walkthrough](../docs/workspace/experiment_walkthrough.md) |
