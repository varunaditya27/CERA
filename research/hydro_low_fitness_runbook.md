# Hydro low-fitness-start runbook

The [protocol](hydro_low_fitness_search_protocol.md) defines the privileged score-derived starting pool and unrestricted later candidate pool. All nine methods are planned for each of three proteins and ten matched seeds. The Gemini arm may incur provider charges; actual billing is not captured by the run records.

For each `PROTEIN` in `P06241`, `P01053` and `P0A9X9`, use the following command with `PROTEIN` replaced literally. Each output directory must be new.

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend python3 scripts/run_matched_proteins.py output/hydro_low_fitness_PROTEIN_141_150 --dataset hydro-PROTEIN --initial-pool train --hydro-low-fitness --seeds 141 142 143 144 145 146 147 148 149 150 --methods random greedy fixed repair gemini_repair ucb ei genetic adalead --specification research/reward_spec_example.json --targeted-disagreement --direct-diversity
```

After all 270 statuses are terminal, use all three roots in both commands. `--resume` checks exact manifest and completed-record fingerprints; interrupted and failed runs are preserved and are not silently replaced.

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend python3 scripts/audit_matched_proteins.py output/hydro_low_fitness_P06241_141_150 output/hydro_low_fitness_P01053_141_150 output/hydro_low_fitness_P0A9X9_141_150 --hydro-low-fitness
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend python3 scripts/evaluate_matched_proteins.py output/hydro_low_fitness_141_150_report.json output/hydro_low_fitness_P06241_141_150 output/hydro_low_fitness_P01053_141_150 output/hydro_low_fitness_P0A9X9_141_150 --specification research/reward_spec_example.json --hydro-low-fitness
```

The special scopes require exactly the three Hydro groups, all methods, the specified seeds, both repair checks, the pinned specification and matching code and software versions. The audit checks initial scores and subsequent selections and reveals, and the evaluator records the later selections' split membership. The model receives split-free candidates and only revealed scores. The audit does not refit all predictors or establish biological warning validity.
