<div align="center">

# Reproducing results

How to rebuild the environment, run the checks and verify saved records

</div>

## Two code layouts

The repository was reorganised after the studies ran. Scripts moved from a flat `scripts/` directory into topic packages, tests moved into area folders, predictor modules moved from `backend/app/experiments/` to `backend/app/predictors/`, and saved results moved from a flat `output/` into topic folders (see the [results index](../../output/README.md)). Saved run records store fingerprints of the code that produced them, so the original layout is kept under the git tag `pre-restructure`.

All audit scripts were re-run on the moved records on 19 November 2026. From the current layout:

| Audit | Result |
| --- | --- |
| Repair comparisons: targeted disagreement, direct diversity, abstention, repair terms, retention, universal penalty, verifier, reactive calibration, later rollback | Pass |
| Rule warning controls, coverage, disagreement and support warning simulations | Pass |
| Four-protein study (360 runs), paired study analysis (80 pairs), Hydro repair diagnosis (363 proposals), Hydro low-fitness summary (270 runs), Hydro and IRED low-change protein audits | Pass |
| Repeated matched Amylase study, advice counts | Pass; the result is confirmed against the audit file saved earlier, and a different result would be an error |
| Held-out shift predictions, mixed held-out predictions, mixed-search comparison, mixed-predictor pilot, exported mixed model | Need the original code; the current code stops with a message that gives the command (see below) |

The last five compare recorded source-file fingerprints. They pass when run with the code they were recorded with: the mixed-search comparison from the `pre-restructure` tag (20 runs, 200 selections), the held-out shift audit from commit `2a81f24` (200 models refitted, 67,660 predictions) the mixed held-out audit from commit `b86eed9` (67,660 predictions), and the two GPU audits from the same tag (the pilot audit refits 3,175 candidates with zero difference from the record; the exported model's refit matches within 4e-9). The held-out audit already failed from the tag, before the reorganisation: `predictor_group.py` changed later on the day its predictions were frozen.

`scripts/reporting/legacy_audit.py` runs an old script from an earlier commit against the current records and cleans up after itself:

```sh
PYTHONPATH=backend:. python3 -m scripts.reporting.legacy_audit audit_mixed_search_comparison \
    output/hybrid/mixed_search_comparison_191_200 configs/reward_spec_example.json /tmp/mixed-audit.json
PYTHONPATH=backend:. python3 -m scripts.reporting.legacy_audit --ref 2a81f24 audit_heldout_shifts \
    output/heldout/heldout_shift_predictions_121_130.json output/heldout/heldout_shift_evaluation_121_130.json
```

## Environment

Python 3.11 or newer is required; the checks in this repository were run with Python 3.14.8.

```sh
python3 -m venv .venv
.venv/bin/pip install -r backend/requirements.txt -r backend/requirements-research.txt -r backend/requirements-embeddings.txt
```

For a CPU-only machine, install the CPU build of PyTorch first; the [README](../../README.md#cpu-only-install) gives the command. Set `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1` before running study scripts so numerical results match the recorded ones. GPU runs in the tested environment also need `TORCH_DISABLE_NATIVE_JIT=1`.

## Running scripts

Scripts are modules of the `scripts` package. Run them from the repository root with both `backend` and the repository root on `PYTHONPATH`:

```sh
PYTHONPATH=backend:. python3 -m scripts.data.audit_data
PYTHONPATH=backend:. python3 -m scripts.multiprotein.run_matched_proteins --help
```

Scripts that write results refuse to overwrite an existing directory or file. Choose a new path under `output/`.

## Tests

```sh
PYTHONPATH=backend:. python3 -m unittest discover -s backend/tests -t backend
```

The checks use a fake model, need no GPU and download no checkpoint. 193 tests passed in about 45 seconds on 19 November 2026. Run one area with `-s backend/tests/rewards`, or one test with its dotted name, for example `tests.rewards.test_reward`.

## Data

`scripts/data/download_data.py` downloads the three primary FLIP2 splits and checks SHA-256 hashes, gzip integrity, columns and row counts. `scripts/data/download_optional_data.py` restores the GB1 and ProteinGym GFP files, and `scripts/data/audit_data.py` checks all five extracted datasets. Sources and licences are in [data/SOURCES.md](../../data/SOURCES.md).

## Saved results

`output/` holds the generated records. [Its index](../../output/README.md) lists which document describes each folder. Most of it is generated data. The web application reads only a few files from it, such as the mixed-search audit shown on the results page.

## Report

The report source is `report/CERA_final_report.tex` and needs XeLaTeX. Build it into a scratch directory, then copy the PDF back:

```sh
latexmk -xelatex -outdir=/tmp/cera-report report/CERA_final_report.tex
cp /tmp/cera-report/CERA_final_report.pdf report/
```

The architecture figure `report/figures/architecture.pdf` is generated from `docs/diagrams/architecture.svg` with `rsvg-convert -f pdf`.
