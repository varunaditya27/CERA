# Multi-protein runbook for review

This is a proposed execution plan, not permission to run it or a frozen study. It implements the [comparison draft](multiprotein_comparison_draft.md) with the full nine-method scope selected by Varun. No output paths below existed when checked on 17 November 2026. The IRED and three Hydro representation cache fingerprints matched their recorded pins in that check. Recheck paths, free space, model availability, account quota and pricing immediately before execution.

Run the following as four separate commands from the repository root, using the same checked-out code, specification and Python environment throughout. They create new directories and do not evaluate the full pool:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend python3 scripts/run_matched_proteins.py output/matched_eval_51_60_ired --dataset ired --seeds 51 52 53 54 55 56 57 58 59 60 --methods random greedy fixed repair gemini_repair ucb ei genetic adalead --specification research/reward_spec_example.json --targeted-disagreement --direct-diversity
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend python3 scripts/run_matched_proteins.py output/matched_eval_51_60_hydro-P06241 --dataset hydro-P06241 --seeds 51 52 53 54 55 56 57 58 59 60 --methods random greedy fixed repair gemini_repair ucb ei genetic adalead --specification research/reward_spec_example.json --targeted-disagreement --direct-diversity
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend python3 scripts/run_matched_proteins.py output/matched_eval_51_60_hydro-P01053 --dataset hydro-P01053 --seeds 51 52 53 54 55 56 57 58 59 60 --methods random greedy fixed repair gemini_repair ucb ei genetic adalead --specification research/reward_spec_example.json --targeted-disagreement --direct-diversity
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend python3 scripts/run_matched_proteins.py output/matched_eval_51_60_hydro-P0A9X9 --dataset hydro-P0A9X9 --seeds 51 52 53 54 55 56 57 58 59 60 --methods random greedy fixed repair gemini_repair ucb ei genetic adalead --specification research/reward_spec_example.json --targeted-disagreement --direct-diversity
```

The Gemini method can make hosted requests and may incur charges. The advisor receives warning types and sanitized menu information, not sequences or scores. Preserve provider failures and fallbacks. A run may fail, stop early, exhaust its budget or have no permitted neighbors; none should be silently replaced. Resume uses the same full command with `--resume`, checks inputs and completed-record fingerprints, and does not retry failed or interrupted runs. Investigate partial or failed work without overwriting its records.

After **all four groups** have terminal statuses, audit their saved decisions and only then evaluate all four together:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend python3 scripts/audit_matched_proteins.py output/matched_eval_51_60_ired output/matched_eval_51_60_hydro-P06241 output/matched_eval_51_60_hydro-P01053 output/matched_eval_51_60_hydro-P0A9X9
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend python3 scripts/evaluate_matched_proteins.py output/matched_eval_51_60_report.json output/matched_eval_51_60_ired output/matched_eval_51_60_hydro-P06241 output/matched_eval_51_60_hydro-P01053 output/matched_eval_51_60_hydro-P0A9X9 --specification research/reward_spec_example.json
```

The audit reconstructs decisions from saved predictions, plus representative sequence-proposal and distance checks; it does not refit predictors or validate scientific assumptions. The evaluator preserves missing comparisons for failed/interrupted runs, reports actual stops and the approved recovery summaries, and does not overwrite an existing report. Both normally require all four groups to be terminal. Results must be reported separately by protein, including unsuccessful runs and all limitations in the draft protocol.

Software preflight so far: 92 backend tests passed, including synthetic nine-method IRED-format and two-method Hydro-format workflows, terminal-status and altered-record checks. The model service and full multi-protein workload were not exercised by those tests. A formal independent two-axis branch review has not been completed.
