<div align="center">

# Web workspace

Prediction, local experiments and goal compilation

</div>

The web workspace shows a read-only summary of the audited mixed-predictor search at `/results` and can predict Amylase sequences at `/predict`. The prediction tool requires the research dependencies, saved model and verified representation cache; it accepts complete sequences with at most four substitutions from the reference. For uncached sequences it also requires the pinned representation-model files in the local Hugging Face cache; it verifies those files and checks three cached examples before generating a representation. No sequence is sent to an external provider. GPU execution in this environment requires starting the backend with `TORCH_DISABLE_NATIVE_JIT=1`. It returns predictions rather than measured scores and marks whether the sequence was used in fitting or range setting. This development model is not validated for laboratory decisions. If its pinned audit is missing or changed, the results endpoint reports it unavailable.

At `/experiments`, run a bounded local search on Amylase, IRED, or one of the three hydrophobic-core proteins with the fixed reward, rule-based repair or optional Gemini-assisted repair; wider studies still use the command-line scripts. The default predictor group has five ridge models; an experimental Amylase-only option uses three ridge models and two neural networks, on the GPU when CUDA is available and otherwise on CPU. The actual device is recorded. A GPU execution failure does not silently retry on CPU. Starting observations come from the source training group and later selections can come from all eligible variants with at most four changes. Hydrophobic-core training membership is based on measured fitness, so its start is not blind.

Each web run saves a separate record under `output/web_runs/`, and incomplete records remain there if a run fails. Completed runs can be opened from the recent-runs list to review selected measurements, predictions, warnings and repair checks.

The review verifies saved scores and chronology against the source dataset. An optional [decision check](../workspace/local_decision_audit.md) also reconstructs selections and repair replays from recorded predictions; it does not independently refit models or prove warning validity.

One local web run may execute at a time.

Recent runs show running while that run holds its operating-system lock and incomplete when it stops without a summary; older records without a per-run lock remain uncertain. Reload the page to refresh status. A browser timeout does not necessarily stop a run, and restarting the backend does not resume an interrupted run.

This is a single-user local feature without authentication: bind both frontend and backend to loopback, and do not expose them publicly or through a remote proxy.

Gemini-assisted repair reads `GEMINI_API_KEY` and `GEMINI_MODEL` from the environment or `backend/.env`, may make billable provider calls, and falls back to a local choice when provider advice fails. The page reports attempted calls and fallbacks; known token counts are not a billing total. The fixed and rule-based experiment options make no Gemini repair calls.

At `/goals`, you may optionally send a fitness-maximization goal to Gemini, review its proposed weights, and select the saved specification for an experiment. Goal text is sent to Google and stored in `output/web_goals/`; do not enter secrets. Compilation may incur charges. The saved specification is fingerprint-checked at run time, and its goal and weights are recorded with the run.
