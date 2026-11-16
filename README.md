# CERA
A framework for auditing, diagnosing, and repairing unreliable learned rewards in protein fitness optimization through counterexample-guided analysis, uncertainty estimation, and constrained LLM-assisted repair.

## Dataset setup

The three primary FLIP2 splits described in the synopsis are stored under `data/raw/flip2/` as both compressed archives and extracted CSV files:

| Landscape | Split | Role | Rows in downloaded split | License |
| --- | --- | --- | ---: | --- |
| Alpha amylase | close-to-far | Development | 3,706 | MIT |
| Imine reductase (IRED) | two-to-many | Test | 8,586 | CC BY 4.0 |
| Hydrophobic core | low-to-high | Test | 24,935 | CC BY 4.0 |

Run `python3 scripts/download_data.py` to download missing files and check SHA-256 hashes, gzip integrity, columns, and row counts. Python 3 standard library is sufficient. If an existing file fails validation, inspect it before replacing it. Source: [FLIP2 benchmark](https://flip.protein.properties/) and [archived dataset and provenance](https://zenodo.org/records/18433203). See [dataset sources and attribution](data/SOURCES.md) for the original datasets, publications, licenses, and direct split links.

The FLIP2 site describes 17,143 IRED variants, but the downloaded two-to-many split contains 8,586 rows. Do not assume the split contains the full landscape; investigate the source and filtering before drawing conclusions. Hydro contains three wild types; whether to search them separately remains an open design decision. The optional GB1 split and ProteinGym GFP assay are also included; see the [usability audit](data/USABILITY.md) for limitations and preparation steps.

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

## Amylase measurement runner

The local Python runner is separate from the web catalog. It selects initial amylase measurements and reveals requested eligible variants within a budget. Separate development modules provide prediction, selection, ranges and warning checks; repair is not yet implemented. The runner's design and limits are documented in the [development protocol](research/amylase_development_protocol.md).

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

An exploratory reference run is in `output/amylase_comparison_seed1_final/`. It is one run, not evidence of an overall winner or a test of CERA's repair system. Later repeated runs, prediction ranges and development warnings are documented in the [work log](research/project_decisions_and_work_log.md); repairs remain future work. A failed or interrupted comparison may leave a partial output directory; inspect its records before using them.

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

## Exploratory prediction ranges

After installing both sets of research requirements, run the amylase range pilot into a new directory:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend .venv/bin/python scripts/run_prediction_pilot.py output/my-range-pilot --seed 1
```

The pilot verifies the exact recorded amylase cache fingerprint, then uses five ridge predictors on the ESM-2 representations. The first 20 reserved measurements set a symmetric prediction range; the predictor group is fitted using the remaining initial measurements and subsequently revealed measurements. Each candidate's prediction, model spread and range are recorded before a score is revealed. The output includes the full run record and a table of observed coverage and range width. See [pilot findings](research/prediction_range_pilot_findings.md) for the initial result and its limits. The nominal 90% target is not guaranteed for this adaptive search. The pilot is pinned to the checked cache; replacing or regenerating that file requires explicitly reviewing and updating the expected fingerprint.

The pilot also records five development warning checks. Member predictions and distance evidence are saved before scores are revealed; range-miss and coverage checks are recorded afterward. `unavailable` means the evidence is insufficient or a calculation is undefined, not that a check passed. The rules, starting thresholds and replay limitations are explained in the [warning findings](research/warning_checks_findings.md).

The same pilot can use the experimental `ucb` and `ei` acquisition rules. Their formulas, assumptions, matched development results and commands are in [acquisition baseline findings](research/acquisition_baseline_findings.md).

Finite-pool recombination and AdaLead-style options are also available through `--local-search`; their proposal rules, sparse-neighborhood stopping behavior and development results are in [local-search findings](research/local_search_baselines_findings.md).

To retrospectively replay the checks on the ten earlier range runs, use a new output directory:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend .venv/bin/python scripts/replay_warnings.py output/amylase_ranges_repeated output/my-warning-replay
```

Replay requires the pinned representation cache and Git history containing commit `78fce61`; it verifies historical code and record fingerprints before rebuilding the predictor groups. Replay writes new evidence and never changes the original runs. It does not implement repairs or establish detection accuracy.

## Reward foundation

The development reward validator and constrained batch selector are described in [reward foundation](research/reward_foundation.md). A separate [reward pilot](research/reward_pilot_findings.md) connects them to the amylase experiment. An experimental rule-based [repair pilot](research/repair_pilot_findings.md) records warning handling and can stop early after repeated failed changes.

The [Gemini goal compiler](research/gemini_goal_compiler.md) can propose the three allowed reward weights and save a validated, replayable specification. It supports the current fixed fitness goal and uses a rule-based fallback. An experimental [Gemini-assisted repair pilot](research/gemini_repair_pilot.md) lets the model prioritize a fixed menu while retaining local verification.
