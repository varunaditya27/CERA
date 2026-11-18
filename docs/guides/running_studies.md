<div align="center">

# Running studies

Command-line runners, comparisons and audits

</div>

## Multi-protein comparison preparation

The staged runner `scripts/multiprotein/run_matched_proteins.py` supports the available protein groups and explicitly requested methods and seeds. By default it chooses starting measurements from sorted eligible sequence identifiers without using benchmark split labels, and records input, representation-cache, software and code fingerprints. It writes compressed run records and per-run status; it does not evaluate the hidden full-pool outcomes. See `PYTHONPATH=backend:. python3 -m scripts.multiprotein.run_matched_proteins --help` for arguments. Resume verifies inputs and completed-record fingerprints; failed or interrupted runs are retained for inspection, not automatically retried.

The runner has completed a 360-run four-protein comparison, a 90-run IRED low-change-start study and a 270-run Hydro low-fitness-start study. These are retrospective, exploratory evaluations, not new laboratory experiments or official FLIP2 benchmark scores. Results, settings and limitations are in the [four-protein findings](../studies/multiprotein/four_protein_findings.md), [IRED findings](../studies/multiprotein/ired_low_change.md#findings), and [Hydro findings](../studies/multiprotein/hydro_low_fitness.md#findings). The Hydro starting split is based on measured fitness and therefore uses privileged information. A seeded sample may differ across Python versions, so the manifest records the Python version; see [Python's reproducibility notes](https://docs.python.org/3/library/random.html#notes-on-reproducibility).

After all configured runs have a terminal status, `scripts/multiprotein/evaluate_matched_proteins.py` can produce a new JSON report from the four protein-group directories and `scripts/multiprotein/audit_matched_proteins.py` can independently reconstruct saved selections and repair replays. Both require all four groups by default and check every supplied group's run statuses before opening outcome files. The separate `--ired-low-change` and `--hydro-low-fitness` scopes validate their respective study protocols; `--allow-partial-development` is only for explicitly labeled development checks. Use each script's `--help` for arguments. The evaluator preserves failed and interrupted statuses and reports per-seed differences against fixed reward when available. The audit checks all recorded selections and replays, plus one available local-proposal round per local method and one reward-distance round per protein; it does not refit the predictors or establish that warning thresholds are scientifically valid.

## Amylase measurement runner

The local Python runner is separate from the web catalog. It selects initial amylase measurements and reveals requested eligible variants within a budget. Separate development modules provide prediction, selection, ranges, warnings and experimental checked repairs. The runner's design and limits are documented in the [development protocol](../studies/amylase/development_protocol.md).

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

After installing both research and embedding requirements below, run the focused checks with `PYTHONPATH=backend:. python3 -m unittest discover -s backend/tests -t backend -v`. The ordinary checks use a fake model and do not download a checkpoint or require a GPU.

## First exploratory comparison

Install the additional research dependencies with `.venv/bin/pip install -r backend/requirements-research.txt` after setting up the environment above. These versions require Python 3.11 or newer. From the repository root, run:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend:. .venv/bin/python -m scripts.amylase.compare_amylase output/my-amylase-comparison --seed 1
```

The output directory must not already exist. The command writes separate run records (`.jsonl`) and best-observed-score tables (`.csv`) for random selection and a simple ridge predictor. Both use the same starting set and budget; the predictor holds 20 initial examples aside and fits on the remaining 80 plus later revealed measurements. Its model choices are checked using cross-validation within the fitting data. Each greedy selection record contains its predicted scores before the measurements are revealed. A score table starts at zero new measurements and includes the best starting score.

An exploratory reference run is in `output/amylase/search/amylase_comparison_seed1_final/`. It is one run, not evidence of an overall winner or a test of CERA's repair system. Later repeated runs, prediction ranges, warnings and experimental repairs are documented in the [work log](../history/work_log.md). A failed or interrupted comparison may leave a partial output directory; inspect its records before using them.

## Amylase sequence representations

The representation code converts sequences into 320-number vectors using a fixed ESM-2 checkpoint; it does not predict or store fitness scores. Install `.venv/bin/pip install -r backend/requirements-embeddings.txt` in addition to the research requirements. PyTorch device support depends on the installed build and machine; the checked versions and GPU limitation are documented in [ESM feasibility](../background/esm_feasibility.md).

For the GPU configuration tested here, run the explicit real-model padding check, then create a cache at a new path:

```sh
TORCH_DISABLE_NATIVE_JIT=1 OPENBLAS_NUM_THREADS=1 PYTHONPATH=backend:. .venv/bin/python -m scripts.data.embed_amylase --verify-only --device cuda
TORCH_DISABLE_NATIVE_JIT=1 OPENBLAS_NUM_THREADS=1 PYTHONPATH=backend:. .venv/bin/python -m scripts.data.embed_amylase --device cuda --batch-size 16 --output output/representations/my-amylase-cache.npz
```

The first run can download model files to the normal Hugging Face cache. The output cache contains sequence identifiers, vectors and metadata, including dataset, reference, model-file, code and settings fingerprints; it contains no scores. Writing is atomic and refuses to replace an existing file. A temporary file can remain after a process is forcibly interrupted; the final cache is only linked into place after the write finishes. Use `app.features.representation_cache.load_cache` with the expected ordered identifiers and exact settings to validate a cache before using it. The tested local cache is `output/representations/amylase_esm2_c731040_v2.npz`.

The same embedding command accepts `--dataset ired`. The IRED reference, cache, source checks and outstanding provenance questions are documented in [IRED preparation](../data/ired_preparation.md). Its pilot dispatch is available but is not a completed evaluation.

The three hydrophobic-core proteins are handled separately. Their source checks, references, score-free caches and the score-derived starting-set limitation are documented in [hydrophobic-core preparation](../data/hydro_preparation.md).


## Mixed predictor development

The optional [mixed predictor](../studies/hybrid/hybrid_predictor.md#findings) uses three ridge members and two neural networks, with GPU or CPU training. It is currently restricted to Amylase development and is not part of the completed five-ridge studies. A [reusable development model and inference example](../studies/hybrid/model_export.md#findings) are available; an [exploratory prediction comparison](../studies/hybrid/exported_model_evaluation.md#findings) and [matched search comparison](../studies/hybrid/mixed_search_comparison.md#findings) are available, with important limits.

## Exploratory prediction ranges

After installing both sets of research requirements, run the amylase range pilot into a new directory:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend:. .venv/bin/python -m scripts.amylase.run_prediction_pilot output/my-range-pilot --seed 1
```

The pilot verifies the exact recorded amylase cache fingerprint, then uses five ridge predictors on the ESM-2 representations. The first 20 reserved measurements set a symmetric prediction range; the predictor group is fitted using the remaining initial measurements and subsequently revealed measurements. Each candidate's prediction, model spread and range are recorded before a score is revealed. The output includes the full run record and a table of observed coverage and range width. See [pilot findings](../studies/amylase/prediction_ranges.md#findings) for the initial result and its limits. The nominal 90% target is not guaranteed for this adaptive search. The pilot is pinned to the checked cache; replacing or regenerating that file requires explicitly reviewing and updating the expected fingerprint.

The pilot also records five development warning checks. Member predictions and distance evidence are saved before scores are revealed; range-miss and coverage checks are recorded afterward. `unavailable` means the evidence is insufficient or a calculation is undefined, not that a check passed. The rules, starting thresholds and replay limitations are explained in the [warning findings](../studies/warnings/warning_checks.md#findings).

The same pilot can use the experimental `ucb` and `ei` acquisition rules. Their formulas, assumptions, matched development results and commands are in [acquisition baseline findings](../studies/amylase/acquisition_baselines.md#findings).

Finite-pool recombination and AdaLead-style options are also available through `--local-search`; their proposal rules, sparse-neighborhood stopping behavior and development results are in [local-search findings](../studies/amylase/local_search_baselines.md#findings).

The [repeated matched development comparison](../studies/amylase/repeated_matched.md#findings) records ten amylase seeds across nine methods, including the observed repair stops and Gemini-call accounting. These are not final results on the other proteins.

To retrospectively replay the checks on the ten earlier range runs, use a new output directory:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend:. .venv/bin/python -m scripts.amylase.replay_warnings output/amylase/search/amylase_ranges_repeated output/my-warning-replay
```

Replay requires the pinned representation cache and Git history containing commit `78fce61`; it verifies historical code and record fingerprints before rebuilding the predictor groups. Replay writes new evidence and never changes the original runs. It does not implement repairs or establish detection accuracy.

## Reward foundation

The development reward validator and constrained batch selector are described in [reward foundation](../studies/amylase/reward_foundation.md#reward-specification-and-batch-selection). A separate [reward pilot](../studies/amylase/reward_pilot.md) connects them to the amylase experiment. An experimental rule-based [repair pilot](../studies/repair/repair_pilot.md) records warning handling and can stop early after repeated failed changes.

For Amylase development, `scripts/amylase/run_reward_pilot.py --reactive-calibration` can update range-setting examples after a coverage warning. It is disabled by default and has no formal adaptive-coverage guarantee; see the [development findings](../studies/repair/reactive_calibration.md#findings).

For Amylase development, `scripts/amylase/run_reward_pilot.py --repair --rollback-monitor` can monitor 30 later measurements after an accepted rule change and restore its immediate predecessor after poor observed coverage. This is an experimental rule, not a coverage guarantee; the [development findings](../studies/repair/later_rollback.md#findings) explain its limits.

Two experimental repair checks are opt-in on `scripts/amylase/run_reward_pilot.py`: `--targeted-disagreement` identifies selected candidates with large model-rank disagreement, and `--direct-diversity` checks whether a proposed replay resolves the batch diversity warning. Both require `--repair` or `--gemini-repair`; omitting them preserves the original checks. The [targeted disagreement protocol](../studies/repair/targeted_disagreement.md#protocol), [direct diversity protocol](../studies/repair/direct_diversity.md), and [work log](../history/work_log.md) describe their development results and limitations.

Recheck the two newer saved amylase comparisons from the repository root with:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend:. python3 -m scripts.repair.audit_development_repairs output/amylase/repair/amylase_targeted_disagreement_31_35
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend:. python3 -m scripts.repair.audit_development_repairs output/amylase/repair/amylase_direct_diversity_41_45
```

The audit checks source and run fingerprints, matched starting observations, recorded seeds, choices, disagreement groups and targets, repair replays, measurements, budgets and summary rows. It reconstructs decisions from saved predictions and distances; it does not independently refit predictors, regenerate distances or prove that recorded warnings, calibration and ranking safeguards are scientifically valid.

To inspect recovery after the first coverage warning in a completed saved run:

```sh
PYTHONPATH=backend:. python3 -m scripts.amylase.summarize_recovery output/amylase/repair/amylase_targeted_disagreement_31_35/seed_32/fixed/run.jsonl.gz
```

The report checks later, non-overlapping-with-the-warning observations in windows of 30, records the first window with 26–28 covered scores and includes its mean range width. Later windows can overlap each other. Runs without a warning or enough follow-up are reported separately; recovery does not establish that a repair caused it. See [recovery options](../background/recovery_measurement_options.md).

The [Gemini goal compiler](../workspace/goal_compiler.md#natural-language-goals) can propose the three allowed reward weights and save a validated, replayable specification. It accepts an optional plain-language fitness goal with `--goal`; this text is sent to Gemini and saved in the record. The model may misunderstand the request, so inspect the saved specification before running it. The original fixed-goal mode retains its rule-based fallback; the user-goal mode stops on an unsupported classification or provider failure. An experimental [Gemini-assisted repair pilot](../studies/repair/gemini_repair_pilot.md) lets the model prioritize a fixed menu while retaining local verification.

New local-web and matched-study Gemini repair records include the warning, permitted options, and raw response text returned by the client for each attempted choice. They do not contain the API key. Provider errors are recorded by status; when a response fails before text is returned, its raw body is unavailable. The fixed prompt text remains in the fingerprinted client code rather than being duplicated in each record. Earlier runs did not preserve raw responses, and goal-compilation records still do not preserve every raw reply. Treat saved provider text as untrusted data.
