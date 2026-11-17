# IRED low-change study runbook

Varun selected an unrestricted eligible candidate pool and subsequently authorized implementation and the remaining project work. The [study plan](ired_low_change_study_plan.md) specifies the exploratory low-change start and its limitations. Use the existing pinned reward specification, IRED dataset and representation cache. The Gemini method may incur charges; configured credentials and model were present at preflight, but provider quota and actual billing were not checked.

Run ten seeds and nine methods in a new output directory:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend python3 scripts/run_matched_proteins.py output/ired_low_change_61_70 --dataset ired --initial-pool train --seeds 61 62 63 64 65 66 67 68 69 70 --methods random greedy fixed repair gemini_repair ucb ei genetic adalead --specification research/reward_spec_example.json --targeted-disagreement --direct-diversity
```

The command records a manifest before running and writes a separate status per method and seed. If interrupted, preserve the directory. `--resume` verifies the manifest and completed-record hashes; failed or interrupted statuses are preserved and are not automatically rerun. Investigate any failure and report it without erasing evidence. Do not feed results back into configuration.

After all 90 statuses are terminal, audit before reporting, then evaluate to a new file:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend python3 scripts/audit_matched_proteins.py output/ired_low_change_61_70 --ired-low-change
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend python3 scripts/evaluate_matched_proteins.py output/ired_low_change_61_70_report.json output/ired_low_change_61_70 --specification research/reward_spec_example.json --ired-low-change
```

The special audit and evaluator scopes require exactly IRED, seeds 61–70, all nine methods, both repair checks and the pinned specification. They check the starting pool's mutation limit and match the exact ordered sample; the existing full four-protein scope still requires its original eligible-start settings. The evaluator records mutation counts of selected variants. The independent audit reconstructs recorded decisions but does not refit every predictor or establish the scientific validity of the warnings.
