# CERA
A framework for auditing, diagnosing, and repairing unreliable learned rewards in protein fitness optimization through counterexample-guided analysis, uncertainty estimation, and constrained LLM-assisted repair.

For the current implementation, main results, reproducibility checks and open work, start with the [integrated project status and results](research/project_status_and_results.md). Earlier research notes are dated snapshots.

## Dataset setup

The three primary FLIP2 splits described in the synopsis are stored under `data/raw/flip2/` as both compressed archives and extracted CSV files:

| Landscape | Split | Role | Rows in downloaded split | License |
| --- | --- | --- | ---: | --- |
| Alpha amylase | close-to-far | Development | 3,706 | MIT |
| Imine reductase (IRED) | two-to-many | Test | 8,586 | CC BY 4.0 |
| Hydrophobic core | low-to-high | Test | 24,935 | CC BY 4.0 |

Run `python3 scripts/download_data.py` to download missing files and check SHA-256 hashes, gzip integrity, columns, and row counts. Python 3 standard library is sufficient. If an existing file fails validation, inspect it before replacing it. Source: [FLIP2 benchmark](https://flip.protein.properties/) and [archived dataset and provenance](https://zenodo.org/records/18433203). See [dataset sources and attribution](data/SOURCES.md) for the original datasets, publications, licenses, and direct split links.

The FLIP2 site describes 17,143 IRED variants, but the downloaded two-to-many split contains 8,586 rows. Do not assume the split contains the full landscape; investigate the source and filtering before drawing conclusions. Hydro contains three wild types, which are prepared as separate protein groups; its score-derived starting split requires care. The optional GB1 split and ProteinGym GFP assay are also included; see the [usability audit](data/USABILITY.md) for limitations and preparation steps.

These raw files contain all measured targets. The amylase runner limits scores exposed through its supported interface, but direct file access can still reveal them. The amylase reference, score direction, representations and exploratory models have been checked; IRED and Hydro retain documented provenance questions. See the [research roadmap](research/CERA_research_evidence_and_roadmap.md) and newer entries in the [work log](research/project_decisions_and_work_log.md).

Run `python3 scripts/download_optional_data.py` to restore or verify GB1 and ProteinGym GFP, then `python3 scripts/audit_data.py` to check all five extracted datasets. See [dataset sources](data/SOURCES.md) for citations and licenses.

## Research workspace

The application separates a Next.js interface (`frontend/`) from a read-only FastAPI dataset catalog (`backend/`). It does not run experiments or expose fitness labels. From the repository root:

```sh
python3 -m venv .venv
.venv/bin/pip install -r backend/requirements.txt
.venv/bin/uvicorn app.main:app --app-dir backend --reload
```

In a second terminal, run `cd frontend && npm install && npm run dev`, then visit `http://localhost:3000`. The frontend reads the API server-side at `http://127.0.0.1:8000`; set `CERA_API_URL` for a different API address. API documentation is at `http://127.0.0.1:8000/docs`. Dataset counts are read from the local CSV files, and the interface displays an unavailable state if the API or files are missing.

The frontend has dedicated routes for the overview (`/`), dataset catalog (`/datasets`), individual dataset profiles (`/datasets/[id]`), and the planned research method (`/workflow`). Dataset counts come from the API; the website does not run experiments or display results. Repository-local design and engineering skills are listed in `skills-lock.json`.

Backend code is grouped under `backend/app/`: `api` serves the catalog, `datasets` identifies source files, `features` handles sequence representations, `experiments` runs and evaluates searches, `rewards` contains warning and repair rules, `llm` contains Gemini integrations, `analysis` replays earlier studies, and `provenance` fingerprints source files. `app.main` is a compatibility package for the existing API command.

## Multi-protein comparison preparation

The staged runner `scripts/run_matched_proteins.py` supports the available protein groups and explicitly requested methods and seeds. By default it chooses starting measurements from sorted eligible sequence identifiers without using benchmark split labels, and records input, representation-cache, software and code fingerprints. It writes compressed run records and per-run status; it does not evaluate the hidden full-pool outcomes. See `PYTHONPATH=backend python3 scripts/run_matched_proteins.py --help` for arguments. Resume verifies inputs and completed-record fingerprints; failed or interrupted runs are retained for inspection, not automatically retried.

The runner has completed a 360-run four-protein comparison, a 90-run IRED low-change-start study and a 270-run Hydro low-fitness-start study. These are retrospective, exploratory evaluations, not new laboratory experiments or official FLIP2 benchmark scores. Results, settings and limitations are in the [four-protein findings](research/multiprotein_study_findings.md), [IRED findings](research/ired_low_change_findings.md), and [Hydro findings](research/hydro_low_fitness_search_findings.md). The Hydro starting split is based on measured fitness and therefore uses privileged information. A seeded sample may differ across Python versions, so the manifest records the Python version; see [Python's reproducibility notes](https://docs.python.org/3/library/random.html#notes-on-reproducibility).

After all configured runs have a terminal status, `scripts/evaluate_matched_proteins.py` can produce a new JSON report from the four protein-group directories and `scripts/audit_matched_proteins.py` can independently reconstruct saved selections and repair replays. Both require all four groups by default and check every supplied group's run statuses before opening outcome files. The separate `--ired-low-change` and `--hydro-low-fitness` scopes validate their respective study protocols; `--allow-partial-development` is only for explicitly labeled development checks. Use each script's `--help` for arguments. The evaluator preserves failed and interrupted statuses and reports per-seed differences against fixed reward when available. The audit checks all recorded selections and replays, plus one available local-proposal round per local method and one reward-distance round per protein; it does not refit the predictors or establish that warning thresholds are scientifically valid.

## Amylase measurement runner

The local Python runner is separate from the web catalog. It selects initial amylase measurements and reveals requested eligible variants within a budget. Separate development modules provide prediction, selection, ranges, warnings and experimental checked repairs. The runner's design and limits are documented in the [development protocol](research/amylase_development_protocol.md).

For an interactive run from the repository root, start `PYTHONPATH=backend python3`, then:

```python
from app.datasets.amylase import DATA, REFERENCE
from app.experiments.experiment import Experiment

run = Experiment(DATA, REFERENCE, 'amylase-run.jsonl', seed=1)
print(len(run.revealed), len(run.candidates), run.remaining)
candidate_id = next(iter(run.candidates))
print(run.reveal([candidate_id]))
run.close()
```

The log file must not already exist; choose a new path for each run. It records the dataset and reference fingerprints, settings, initially revealed scores, and each selection before its revealed measurements. The reference sequence was retrieved from the [original source at a fixed commit](https://github.com/florisvdf/mutation-predictability/blob/aea601d50493892fc6a73601beb90b8d0c93cd52/data/AMY_BACSU/reference.fasta). A failed or interrupted log write can leave an incomplete record; inspect it before interpreting the run. The interface prevents accidental score disclosure through its supported methods, but Python code with direct file or object access can still read raw scores.

After installing both research and embedding requirements below, run the focused checks with `PYTHONPATH=backend python3 -m unittest discover -s backend/tests -v`. The ordinary checks use a fake model and do not download a checkpoint or require a GPU.

## First exploratory comparison

Install the additional research dependencies with `.venv/bin/pip install -r backend/requirements-research.txt` after setting up the environment above. These versions require Python 3.11 or newer. From the repository root, run:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend .venv/bin/python scripts/compare_amylase.py output/my-amylase-comparison --seed 1
```

The output directory must not already exist. The command writes separate run records (`.jsonl`) and best-observed-score tables (`.csv`) for random selection and a simple ridge predictor. Both use the same starting set and budget; the predictor holds 20 initial examples aside and fits on the remaining 80 plus later revealed measurements. Its model choices are checked using cross-validation within the fitting data. Each greedy selection record contains its predicted scores before the measurements are revealed. A score table starts at zero new measurements and includes the best starting score.

An exploratory reference run is in `output/amylase_comparison_seed1_final/`. It is one run, not evidence of an overall winner or a test of CERA's repair system. Later repeated runs, prediction ranges, warnings and experimental repairs are documented in the [work log](research/project_decisions_and_work_log.md). A failed or interrupted comparison may leave a partial output directory; inspect its records before using them.

## Amylase sequence representations

The representation code converts sequences into 320-number vectors using a fixed ESM-2 checkpoint; it does not predict or store fitness scores. Install `.venv/bin/pip install -r backend/requirements-embeddings.txt` in addition to the research requirements. PyTorch device support depends on the installed build and machine; the checked versions and GPU limitation are documented in [ESM feasibility](research/esm_feasibility_and_plan.md).

For the GPU configuration tested here, run the explicit real-model padding check, then create a cache at a new path:

```sh
TORCH_DISABLE_NATIVE_JIT=1 OPENBLAS_NUM_THREADS=1 PYTHONPATH=backend .venv/bin/python scripts/embed_amylase.py --verify-only --device cuda
TORCH_DISABLE_NATIVE_JIT=1 OPENBLAS_NUM_THREADS=1 PYTHONPATH=backend .venv/bin/python scripts/embed_amylase.py --device cuda --batch-size 16 --output output/representations/my-amylase-cache.npz
```

The first run can download model files to the normal Hugging Face cache. The output cache contains sequence identifiers, vectors and metadata, including dataset, reference, model-file, code and settings fingerprints; it contains no scores. Writing is atomic and refuses to replace an existing file. A temporary file can remain after a process is forcibly interrupted; the final cache is only linked into place after the write finishes. Use `app.features.representation_cache.load_cache` with the expected ordered identifiers and exact settings to validate a cache before using it. The tested local cache is `output/representations/amylase_esm2_c731040_v2.npz`.

The same embedding command accepts `--dataset ired`. The IRED reference, cache, source checks and outstanding provenance questions are documented in [IRED preparation](research/ired_preparation.md). Its pilot dispatch is available but is not a completed evaluation.

The three hydrophobic-core proteins are handled separately. Their source checks, references, score-free caches and the score-derived starting-set limitation are documented in [hydrophobic-core preparation](research/hydro_preparation.md).

The web workspace shows a read-only summary of the audited mixed-predictor search at `/results` and can predict Amylase sequences at `/predict`. The prediction tool requires the research dependencies, saved model and verified representation cache; it accepts complete sequences with at most four substitutions from the reference. For uncached sequences it also requires the pinned representation-model files in the local Hugging Face cache; it verifies those files and checks three cached examples before generating a representation. No sequence is sent to an external provider. GPU execution in this environment requires starting the backend with `TORCH_DISABLE_NATIVE_JIT=1`. It returns predictions rather than measured scores and marks whether the sequence was used in fitting or range setting. This development model is not validated for laboratory decisions. If its pinned audit is missing or changed, the results endpoint reports it unavailable. At `/experiments`, run a bounded local search on Amylase, IRED, or one of the three hydrophobic-core proteins with the fixed reward, rule-based repair or optional Gemini-assisted repair; wider studies still use the command-line scripts. The default predictor group has five ridge models; an experimental Amylase-only option uses three ridge models and two neural networks, on the GPU when CUDA is available and otherwise on CPU. The actual device is recorded. A GPU execution failure does not silently retry on CPU. Starting observations come from the source training group and later selections can come from all eligible variants with at most four changes. Hydrophobic-core training membership is based on measured fitness, so its start is not blind. Each web run saves a separate record under `output/web_runs/`, and incomplete records remain there if a run fails. Completed runs can be opened from the recent-runs list to review selected measurements, predictions, warnings and repair checks. The review verifies saved scores and chronology against the source dataset but does not independently refit models or prove warning validity. One local web run may execute at a time. Recent runs show running while that run holds its operating-system lock and incomplete when it stops without a summary; older records without a per-run lock remain uncertain. Reload the page to refresh status. A browser timeout does not necessarily stop a run, and restarting the backend does not resume an interrupted run. This is a single-user local feature without authentication: bind both frontend and backend to loopback, and do not expose them publicly or through a remote proxy. Gemini-assisted repair reads `GEMINI_API_KEY` and `GEMINI_MODEL` from the environment or `backend/.env`, may make billable provider calls, and falls back to a local choice when provider advice fails. The page reports attempted calls and fallbacks; known token counts are not a billing total. The fixed and rule-based experiment options make no Gemini repair calls. At `/goals`, you may optionally send a fitness-maximization goal to Gemini, review its proposed weights, and select the saved specification for an experiment. Goal text is sent to Google and stored in `output/web_goals/`; do not enter secrets. Compilation may incur charges. The saved specification is fingerprint-checked at run time, and its goal and weights are recorded with the run.

## Mixed predictor development

The optional [mixed predictor](research/hybrid_predictor_findings.md) uses three ridge members and two neural networks, with GPU or CPU training. It is currently restricted to Amylase development and is not part of the completed five-ridge studies. A [reusable development model and inference example](research/hybrid_model_export_findings.md) are available; an [exploratory prediction comparison](research/exported_model_evaluation_findings.md) and [matched search comparison](research/mixed_search_comparison_findings.md) are available, with important limits.

## Exploratory prediction ranges

After installing both sets of research requirements, run the amylase range pilot into a new directory:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend .venv/bin/python scripts/run_prediction_pilot.py output/my-range-pilot --seed 1
```

The pilot verifies the exact recorded amylase cache fingerprint, then uses five ridge predictors on the ESM-2 representations. The first 20 reserved measurements set a symmetric prediction range; the predictor group is fitted using the remaining initial measurements and subsequently revealed measurements. Each candidate's prediction, model spread and range are recorded before a score is revealed. The output includes the full run record and a table of observed coverage and range width. See [pilot findings](research/prediction_range_pilot_findings.md) for the initial result and its limits. The nominal 90% target is not guaranteed for this adaptive search. The pilot is pinned to the checked cache; replacing or regenerating that file requires explicitly reviewing and updating the expected fingerprint.

The pilot also records five development warning checks. Member predictions and distance evidence are saved before scores are revealed; range-miss and coverage checks are recorded afterward. `unavailable` means the evidence is insufficient or a calculation is undefined, not that a check passed. The rules, starting thresholds and replay limitations are explained in the [warning findings](research/warning_checks_findings.md).

The same pilot can use the experimental `ucb` and `ei` acquisition rules. Their formulas, assumptions, matched development results and commands are in [acquisition baseline findings](research/acquisition_baseline_findings.md).

Finite-pool recombination and AdaLead-style options are also available through `--local-search`; their proposal rules, sparse-neighborhood stopping behavior and development results are in [local-search findings](research/local_search_baselines_findings.md).

The [repeated matched development comparison](research/repeated_matched_findings.md) records ten amylase seeds across nine methods, including the observed repair stops and Gemini-call accounting. These are not final results on the other proteins.

To retrospectively replay the checks on the ten earlier range runs, use a new output directory:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend .venv/bin/python scripts/replay_warnings.py output/amylase_ranges_repeated output/my-warning-replay
```

Replay requires the pinned representation cache and Git history containing commit `78fce61`; it verifies historical code and record fingerprints before rebuilding the predictor groups. Replay writes new evidence and never changes the original runs. It does not implement repairs or establish detection accuracy.

## Reward foundation

The development reward validator and constrained batch selector are described in [reward foundation](research/reward_foundation.md). A separate [reward pilot](research/reward_pilot_findings.md) connects them to the amylase experiment. An experimental rule-based [repair pilot](research/repair_pilot_findings.md) records warning handling and can stop early after repeated failed changes.

For Amylase development, `scripts/run_reward_pilot.py --reactive-calibration` can update range-setting examples after a coverage warning. It is disabled by default and has no formal adaptive-coverage guarantee; see the [development findings](research/reactive_calibration_findings.md).

For Amylase development, `scripts/run_reward_pilot.py --repair --rollback-monitor` can monitor 30 later measurements after an accepted rule change and restore its immediate predecessor after poor observed coverage. This is an experimental rule, not a coverage guarantee; the [development findings](research/later_rollback_findings.md) explain its limits.

Two experimental repair checks are opt-in on `scripts/run_reward_pilot.py`: `--targeted-disagreement` identifies selected candidates with large model-rank disagreement, and `--direct-diversity` checks whether a proposed replay resolves the batch diversity warning. Both require `--repair` or `--gemini-repair`; omitting them preserves the original checks. The [targeted disagreement protocol](research/targeted_disagreement_protocol.md), [direct diversity protocol](research/direct_diversity_protocol.md), and [work log](research/project_decisions_and_work_log.md) describe their development results and limitations.

Recheck the two newer saved amylase comparisons from the repository root with:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend python3 scripts/audit_development_repairs.py output/amylase_targeted_disagreement_31_35
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend python3 scripts/audit_development_repairs.py output/amylase_direct_diversity_41_45
```

The audit checks source and run fingerprints, matched starting observations, recorded seeds, choices, disagreement groups and targets, repair replays, measurements, budgets and summary rows. It reconstructs decisions from saved predictions and distances; it does not independently refit predictors, regenerate distances or prove that recorded warnings, calibration and ranking safeguards are scientifically valid.

To inspect recovery after the first coverage warning in a completed saved run:

```sh
PYTHONPATH=backend python3 scripts/summarize_recovery.py output/amylase_targeted_disagreement_31_35/seed_32/fixed/run.jsonl.gz
```

The report checks later, non-overlapping-with-the-warning observations in windows of 30, records the first window with 26–28 covered scores and includes its mean range width. Later windows can overlap each other. Runs without a warning or enough follow-up are reported separately; recovery does not establish that a repair caused it. See [recovery options](research/recovery_measurement_options.md).

The [Gemini goal compiler](research/natural_goal_compiler.md) can propose the three allowed reward weights and save a validated, replayable specification. It accepts an optional plain-language fitness goal with `--goal`; this text is sent to Gemini and saved in the record. The model may misunderstand the request, so inspect the saved specification before running it. The original fixed-goal mode retains its rule-based fallback; the user-goal mode stops on an unsupported classification or provider failure. An experimental [Gemini-assisted repair pilot](research/gemini_repair_pilot.md) lets the model prioritize a fixed menu while retaining local verification.
