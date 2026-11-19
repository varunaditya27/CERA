# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

CERA is a research project: auditing and repairing unreliable learned rewards in protein fitness optimization. Backend (FastAPI) and the `scripts/` studies are Python; the web UI is Next.js in `frontend/`. Results are retrospective, exploratory evaluations on benchmark data (FLIP2, GB1, GFP), not laboratory experiments. Start from `docs/overview/status_and_results.md`; other notes in `research/` are dated snapshots. The README is long and holds most run commands.

## Commands

All Python runs from the repo root with `PYTHONPATH=backend:.` (the `.` makes the `scripts` package importable). Setup uses `.venv` (Python 3.11+; docs verified on 3.14).

```sh
.venv/bin/pip install -r backend/requirements.txt                 # API only
.venv/bin/pip install -r backend/requirements-research.txt -r backend/requirements-embeddings.txt  # runs, tests

# Backend
.venv/bin/uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000

# Frontend
cd frontend && npm ci && npm run build && npm run start -- --hostname 127.0.0.1
npm run typecheck && npm run format        # tsc --noEmit, prettier

# Tests (unittest, not pytest; fake model, no GPU or checkpoint download)
PYTHONPATH=backend:. python3 -m unittest discover -s backend/tests -t backend
PYTHONPATH=backend:. python3 -m unittest discover -s backend/tests/rewards -t backend   # one area
PYTHONPATH=backend:. python3 -m unittest tests.rewards.test_reward                      # one file

# Scripts are modules of the scripts package, grouped by topic
PYTHONPATH=backend:. python3 -m scripts.data.audit_data

# Report (XeLaTeX)
latexmk -xelatex -outdir=/tmp/cera-report report/CERA_final_report.tex
```

- Set `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1` for reproducible research scripts. GPU runs of scripts here also need `TORCH_DISABLE_NATIVE_JIT=1`; the API sets it itself.
- Audits that compare recorded source fingerprints (mixed-search, held-out shift, mixed held-out, GPU mixed-predictor) detect changed code and re-run themselves from the commit their records were frozen at, via `scripts/reporting/legacy_audit.py` (run from the repo root). Add the same `except CodeChanged: rerun_with_recorded_code(...)` wrapper to any new audit that checks code fingerprints.
- Script output directories and run-log files must not already exist; scripts refuse to overwrite. Pick a new path under `output/`.
- Do not stop servers with `pkill -f`; use `fuser -k 8000/tcp` (see global rules).
- `frontend/AGENTS.md` warns this Next.js version has breaking changes: read `frontend/node_modules/next/dist/docs/` before writing frontend code. The stylesheet follows Hallmark's app-screen rules (tokens only, no literal colours, 4px spacing, no tracked-caps labels); check with `node ~/.claude/skills/hallmark/scripts/sloplint.mjs frontend/app/globals.css --scope app --render --url <route>`, then `npm run check:a11y` (axe-core and a keyboard Tab walk; needs both servers up, `CHROME_PATH` and `CERA_WEB_URL`). Surfaces are separated by tone and space, not 1px lines; real tables and form fields are the exception. Motion is a short staggered entrance (transform and opacity only, with a reduced-motion fallback) at the end of `globals.css`.

## Architecture

`backend/app/` packages:

- `datasets`: identifies and loads source CSVs in `data/raw/` (amylase, IRED, hydro, FLIP2).
- `features`: ESM-2 sequence vectors with a fingerprinted `.npz` cache (`output/representations/`). Caches contain no scores and are validated against exact ordered ids and settings.
- `experiments`: `Experiment` is the measurement runner. It hides scores until a candidate is revealed within a budget and logs each selection before its revealed result. Also holds selection, acquisition rules, local search and evaluation.
- `predictors`: ridge group, mixed (ridge plus neural) predictor, prediction ranges and calibration.
- `rewards`: reward spec, warning checks, rule-based repair engine, rollback monitor, repair coordinator.
- `llm`: Gemini integrations (goal compiler, repair advisor). Repairs are menu-limited and locally verified, with a local fallback when the provider fails.
- `analysis`: replays and audits saved studies from their records.
- `provenance`: fingerprints source files and code.
- `workspace`: services behind the web "experiments" and "goals" pages (run, review, audit).
- `api`: FastAPI routes. `app.main` is a compatibility package so the uvicorn command stays unchanged.

`scripts/<topic>/` (data, amylase, repair, warnings, multiprotein, hybrid, heldout, reporting) holds the study pipeline: `run_*` produce compressed run records (`.jsonl.gz`), `evaluate_*` and `summarize_*` build reports, `audit_*` independently reconstruct decisions from saved records, `compare_*` run matched comparisons. Saved results live in `output/` (index in `output/README.md`; never edit or rename records). Docs are under `docs/` (overview, guides, studies by topic, glossary, history), the report in `report/`, the slides in `presentation/`, brand files in `assets/brand/`, and `configs/reward_spec_example.json` is the fingerprinted default reward spec.

## Conventions that matter

- Provenance first: records store fingerprints of data, caches, code and software. Replays and audits verify them before use, and may need specific git history (for example commit `78fce61` for warning replay). Records written before the reorganisation are verified from the git tag `pre-restructure`. Changing a pinned cache or checked code means deliberately updating the expected fingerprint.
- Score exposure: the runner limits scores through its interface, but raw CSVs contain all targets. Keep new code from reading hidden scores before reveal. Hydro starting splits use measured fitness, so those starts are not blind.
- Failed or interrupted runs are kept for inspection, never silently retried. A GPU failure does not fall back to CPU.
- The web workspace is single-user, no authentication, one run at a time. Bind both servers to loopback only. Gemini features read `GEMINI_API_KEY` and `GEMINI_MODEL` from the environment or `backend/.env`, send goal text to Google, and may bill.
- Findings docs state limits explicitly (not final results, not official benchmark scores, no coverage guarantees). Keep claims in docs and UI text consistent with that.
