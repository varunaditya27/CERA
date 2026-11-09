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

These raw files contain all measured targets. A future experiment must enforce label hiding in its query interface; storing the files here does not itself prevent leakage. Target direction and wild-type metadata still need verification before experiments. Embeddings and models have not been generated.

Run `python3 scripts/download_optional_data.py` to restore or verify GB1 and ProteinGym GFP, then `python3 scripts/audit_data.py` to check all five extracted datasets. See [dataset sources](data/SOURCES.md) for citations and licenses.

## Research workspace

The application separates a Next.js interface (`frontend/`) from a read-only FastAPI dataset catalog (`backend/`). It does not run experiments or expose fitness labels. From the repository root:

```sh
python3 -m venv .venv
.venv/bin/pip install -r backend/requirements.txt
.venv/bin/uvicorn app.main:app --app-dir backend --reload
```

In a second terminal, run `cd frontend && npm install && npm run dev`, then visit `http://localhost:3000`. The frontend reads the API server-side at `http://127.0.0.1:8000`; set `CERA_API_URL` for a different API address. API documentation is at `http://127.0.0.1:8000/docs`. Dataset counts are read from the local CSV files, and the interface displays an unavailable state if the API or files are missing.

The frontend has dedicated routes for the overview (`/`), dataset catalog (`/datasets`), individual dataset profiles (`/datasets/[id]`), and the planned research method (`/workflow`). Dataset counts come from the API; experiment execution and results are not implemented yet. Repository-local design and engineering skills are listed in `skills-lock.json`.
