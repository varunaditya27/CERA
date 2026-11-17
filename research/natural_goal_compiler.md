# Natural-language fitness goal compilation

The goal compiler now accepts an optional short user description of a protein fitness search. Gemini receives the text as part of a request and proposes the three permitted reward weights. The application constructs and validates the specification locally: the objective remains `maximize_fitness`, and the existing mutation limit, budget, allowed weight ranges and stopping limit cannot be changed by the model. No protein sequence or measured score is sent by the compiler unless the user includes it in their own text. The goal text is saved in the output record, so do not include secrets or material you do not want sent to the provider and stored locally.

The model is instructed to flag unsupported objectives, changes to constraints or budgets, and unrelated requests. A flagged goal is rejected; invalid output is retried once, while service or configuration errors stop the command. Unlike the original fixed-goal mode, this path does not fall back to a generic specification. **The model can still misunderstand a request or misclassify it as supported.** Inspect the saved specification and verify that its fixed limits and weights reflect the intended task before using it. The validator checks the structure and bounds; it cannot prove that the model interpreted the words correctly or that the proposed weights are effective. Google's [structured-output documentation](https://ai.google.dev/gemini-api/docs/structured-output) likewise requires application validation and handling semantically incorrect results.

From the repository root, using a new path for each output:

```sh
PYTHONPATH=backend python3 scripts/compile_reward_goal.py output/my-goal.json --goal 'Maximize protein fitness while favoring diverse batches.'
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend python3 scripts/run_reward_pilot.py output/my-run output/my-goal.json --dataset amylase --seed 13 --repair --targeted-disagreement --direct-diversity
```

The first command uses `GEMINI_API_KEY` and `GEMINI_MODEL` from the environment or ignored `backend/.env`, sends a provider request, and may incur charges. The second uses the saved specification; it makes no Gemini repair calls unless `--gemini-repair` is explicitly selected. Omitting `--goal` preserves the previous fixed-goal behavior and its documented fallback. A user goal that changes hard limits or asks for a different objective is outside the current supported domain.

## Verification

A live request for fitness maximization with diversity produced the saved [validated specification](../output/natural_goal_check.json), with 141 provider-reported tokens. The saved file was used in a real Amylase run with rule-based repair; it stopped after two failed repair actions and 20 new measurements. A separate check recomputed the run summary against the source scores, checked the input fingerprint and confirmed 20/20 recorded intervals covered their associated scores. This is a functional check of one run, not an independent model benchmark, repair benefit or coverage guarantee. A separate live request for fitness minimization was rejected as unsupported; its token usage and actual billing were not captured.

Four focused tests cover validated output, fixed limits, unsupported and unavailable responses, malformed or duplicated fields, goal length, request construction and passing the saved goal into the pilot. All 150 backend tests passed. Hosted-model responses can change; the live checks do not prove reliable classification for every natural-language request.

## Local web workflow

The local workspace provides a Goals page to compile and review a short goal before selecting it on the Experiments page. The full goal text is sent to Gemini and saved under `output/web_goals/`; requests may incur charges. The backend rejects a saved file whose fingerprint changed since it was selected, validates the three bounded weights and the fixed constraints, and records the goal and specification in the run. This prevents accidental use of a changed file, not semantic mistakes by Gemini. A live web flow compiled a sample goal with one accepted provider request and 138 reported tokens, displayed its weights, used the saved specification in an Amylase run, and retained it in the run review. This is an engineering check, not a validated interpretation or proof of fitness improvement.
