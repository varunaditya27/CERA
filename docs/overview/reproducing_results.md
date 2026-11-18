<div align="center">

# Reproducing results

How to rebuild the environment, run the checks and verify saved records

</div>

## Two code layouts

The repository was reorganised after the studies ran. Scripts moved from a flat `scripts/` directory into topic packages, tests moved into area folders, and predictor modules moved from `backend/app/experiments/` to `backend/app/predictors/`. Saved run records store fingerprints of the code that produced them, so the original layout is kept under the git tag `pre-restructure`.

- Run new work from the current layout.
- To re-verify a record written before the reorganisation with its original scripts, check out the tag in a separate worktree and run the old `scripts/<name>.py` there against the same `output/` folder:

```sh
git worktree add ../CERA-pre pre-restructure
cd ../CERA-pre
PYTHONPATH=backend python3 scripts/audit_development_repairs.py ../CERA/output/amylase_targeted_disagreement_31_35
```

The same audit also passes from the current layout (`PYTHONPATH=backend:. python3 -m scripts.repair.audit_development_repairs output/amylase_targeted_disagreement_31_35`); both runs reported 10 runs, 72 selections and 30 repair replays when this document was written.

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

The checks use a fake model, need no GPU and download no checkpoint. 189 tests passed in about 45 seconds at the time of the reorganisation. Run one area with `-s backend/tests/rewards`, or one test with its dotted name, for example `tests.rewards.test_reward`.

## Data

`scripts/data/download_data.py` downloads the three primary FLIP2 splits and checks SHA-256 hashes, gzip integrity, columns and row counts. `scripts/data/download_optional_data.py` restores the GB1 and ProteinGym GFP files, and `scripts/data/audit_data.py` checks all five extracted datasets. Sources and licences are in [data/SOURCES.md](../../data/SOURCES.md).

## Saved results

`output/` holds the generated records. [Its index](../../output/README.md) lists which document describes each folder. Most of it is generated data. The web application reads only a few files from it, such as the mixed-search audit shown on the results page.
