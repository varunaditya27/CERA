<div align="center">

# Demo walkthrough

A five-minute path through the workspace, checked on 19 November 2026

</div>

## Start

```sh
.venv/bin/uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
cd frontend && npm ci && npm run build && npm run start -- --hostname 127.0.0.1
```

Open `http://127.0.0.1:3000`. Setup, the research requirements and a CPU-only install are in the [setup guide](setup.md). The API sets `TORCH_DISABLE_NATIVE_JIT=1` itself, so nothing else needs exporting.

## Steps

1. **Overview and datasets.** The overview shows the primary-study tally. Datasets lists five landscapes; open one for its purpose and preparation notes.
2. **Results.** Bar charts of the recorded primary study and of the mixed-versus-ridge range coverage, each with its table.
3. **Predict.** Paste an Amylase sequence of 425 letters with at most four substitutions from the reference (`data/amylase_reference.fasta`). With one substitution at position 11, the page returned a predicted score of 0.0645 with a range of -0.0320 to 0.1610, generated on the GPU in a few seconds. It states that the range is an estimate and that the development model is not validated for laboratory decisions.
4. **Experiments.** Choose Imine reductase (IRED), seed 7, fixed reward, five ridge models, and run it. It finished in seconds: 100 new measurements, best observed score 1.8038, 96 of 100 scores inside their predicted ranges, no repairs.
5. **Review.** Open the run from the recent-runs list. Each of the 10 batches opens to its warnings, repair decisions and a table of revealed scores with their pre-reveal predictions.
6. **Decision check.** From the review, choose "Check recorded decisions". It passes (10 batch selections checked, 0 repair replays for a fixed-reward run).
7. **Mixed predictor.** Choose Alpha amylase, seed 8, rule-based repair and the three-ridge plus two-network group. It trains on the GPU and finished with 20 new measurements and 18 of 20 scores in range.
8. **Goals.** Compiling a goal calls Gemini and needs `GEMINI_API_KEY` and `GEMINI_MODEL` in `backend/.env`; the goal text is sent to Google and the call may bill. Entering "Find the Amylase variant with the highest activity while staying close to known sequences." produced an uncertainty penalty of 0.5, a distance penalty of 1 and a diversity bonus of 0, up to 4 sequence changes, 10 batches of 10. It appears under Saved goals and as a choice on Experiments; a fixed-reward Amylase run with it (seed 9) finished with 100 new measurements and best score 0.2012. The weights depend on the model's reply and can differ between calls; review them before use.

Runs are saved under `output/web_runs/` (ignored by git). The workspace is single-user and has no authentication; keep both servers on the loopback address.

## What was checked

A browser run covered every route plus steps 3 to 8 with no console errors and no failed requests; `npm run check:a11y` passes on all routes at desktop and phone width. The numbers above are deterministic for the seeds shown.
