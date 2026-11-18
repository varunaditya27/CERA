<div align="center">

# Setup

Install the data, backend and frontend

</div>

## Datasets

The three primary FLIP2 splits described in the synopsis are stored under `data/raw/flip2/` as both compressed archives and extracted CSV files:

| Landscape | Split | Role | Rows in downloaded split | License |
| --- | --- | --- | ---: | --- |
| Alpha amylase | close-to-far | Development | 3,706 | MIT |
| Imine reductase (IRED) | two-to-many | Test | 8,586 | CC BY 4.0 |
| Hydrophobic core | low-to-high | Test | 24,935 | CC BY 4.0 |

Run `python3 -m scripts.data.download_data` to download missing files and check SHA-256 hashes, gzip integrity, columns, and row counts. Python 3 standard library is sufficient. If an existing file fails validation, inspect it before replacing it. Source: [FLIP2 benchmark](https://flip.protein.properties/) and [archived dataset and provenance](https://zenodo.org/records/18433203). See [dataset sources and attribution](../../data/SOURCES.md) for the original datasets, publications, licenses, and direct split links.

The FLIP2 site describes 17,143 IRED variants, but the downloaded two-to-many split contains 8,586 rows: only measured-active variants without flagged insertions, deletions or stop codons (see [IRED preparation](../data/ired_preparation.md)). It does not contain the full screened landscape. Hydro contains three wild types, which are prepared as separate protein groups; its score-derived starting split requires care. The optional GB1 split and ProteinGym GFP assay are also included; see the [usability audit](../../data/USABILITY.md) for limitations and preparation steps.

These raw files contain all measured targets. The amylase runner limits scores exposed through its supported interface, but direct file access can still reveal them. The amylase reference, score direction, representations and exploratory models have been checked; the IRED split selection is explained in [IRED preparation](../data/ired_preparation.md) (two small questions remain), and the Hydro references and scores were matched to the original authors' table in [Hydro preparation](../data/hydro_preparation.md); only the laboratory construct details behind the Hydro proteins were not independently confirmed. See the [research roadmap](../overview/roadmap.md) and newer entries in the [work log](../history/work_log.md).

Run `python3 -m scripts.data.download_optional_data` to restore or verify GB1 and ProteinGym GFP, then `python3 -m scripts.data.audit_data` to check all five extracted datasets. See [dataset sources](../../data/SOURCES.md) for citations and licenses.

## Backend and frontend

The application combines a Next.js interface (`frontend/`) with a FastAPI backend (`backend/`). The backend serves the dataset catalog, saved study results and the local experiment workflow. From the repository root:

```sh
python3 -m venv .venv
.venv/bin/pip install -r backend/requirements.txt
.venv/bin/uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
```

In a second terminal, run `cd frontend && npm ci && npm run build && npm run start -- --hostname 127.0.0.1`, then visit `http://127.0.0.1:3000`. The frontend reads the API at `http://127.0.0.1:8000`. Set `CERA_API_URL` for a different API address. API documentation is at `http://127.0.0.1:8000/docs`. Dataset counts come from the local CSV files.

The frontend has dedicated routes for the overview (`/`), dataset catalog (`/datasets`), individual dataset profiles (`/datasets/[id]`), and the research method (`/workflow`). Visit `/results` for the primary four-protein and Amylase comparisons and `/experiments` for local runs and their reviews. The setup above serves the catalog and saved comparisons. Install the research and embedding requirements before starting a run.

### CPU-only install

For a CPU-only demo, the following commands were verified with Python 3.14.8 and `uv` in a fresh environment. Run them inside the repository root with the backend stopped, then restart it. The Amylase fixed-reward demo uses the checked-in representation cache.

```sh
uv pip install --python .venv/bin/python --index-url https://download.pytorch.org/whl/cpu 'torch==2.14.0'
uv pip install --python .venv/bin/python -r backend/requirements-research.txt -r backend/requirements-embeddings.txt
```

For the demo input and expected result, see the [experiment walkthrough](../overview/submission_readiness.md#experiment-demonstration). [PyTorch installation guide](https://pytorch.org/get-started/locally/) · [npm clean install](https://docs.npmjs.com/cli/v11/commands/npm-ci/)

Backend code is grouped under `backend/app/`: `api` serves the catalog, `datasets` identifies source files, `features` handles sequence representations, `experiments` runs and evaluates searches, `rewards` contains warning and repair rules, `llm` contains Gemini integrations, `analysis` replays earlier studies, and `provenance` fingerprints source files. `app.main` is a compatibility package for the existing API command.
