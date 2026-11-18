<div align="center">

# Reproducing results

How to rebuild the environment, run the checks and verify saved records

</div>

## Two code layouts

The repository was reorganised after the studies ran. Scripts moved from a flat `scripts/` directory into topic packages, tests moved into area folders, predictor modules moved from `backend/app/experiments/` to `backend/app/predictors/`, and saved results moved from a flat `output/` into topic folders (see the [results index](../../output/README.md)). Saved run records store fingerprints of the code that produced them, so the original layout is kept under the git tag `pre-restructure`.

Checked after the reorganisation, against the moved records:

| Audit | From the current layout |
| --- | --- |
| Targeted-disagreement repair comparison (10 runs, 72 selections, 30 replays) | Passes |
| IRED low-change study (90 runs, 703 selections, 135 repair replays) | Passes |
| Mixed-search comparison (20 runs, 200 selections) | Fails with `Method or source mismatch`: it compares recorded source-file fingerprints, which changed when the code moved |
| Mixed-search comparison, original script from the tag | Passes (20 runs, 200 selections, 10 ties) |

Audits of the second kind need the original code. Check it out without the large result files and point it at the current records:

```sh
git worktree add --no-checkout ../CERA-pre pre-restructure
cd ../CERA-pre && git sparse-checkout set --no-cone backend scripts research data && git checkout
mkdir output && ln -s ../CERA/output/representations output/representations
PYTHONPATH=backend python3 scripts/audit_mixed_search_comparison.py ../CERA/output/hybrid/mixed_search_comparison_191_200 research/reward_spec_example.json /tmp/mixed-audit.json
```

Other audits were not all re-run after the move. If one reports a source or fingerprint mismatch, run it from the tag in the same way.

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

The checks use a fake model, need no GPU and download no checkpoint. 191 tests passed in about 45 seconds on 19 November 2026. Run one area with `-s backend/tests/rewards`, or one test with its dotted name, for example `tests.rewards.test_reward`.

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
