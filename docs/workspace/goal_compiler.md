<div align="center">

# Goal compilation with Gemini

Design and usage

</div>

## Reward-weight compilation

This is a historical record of the fixed-goal implementation. The later [natural-language goal path](goal_compiler.md#natural-language-goals) adds optional user goal text; this file preserves the original check and results.

Implemented and checked 16 November 2026. This is a constrained first version of the language-model component, not the complete LLM-assisted repair system.

### What the model can do

The current project has one supported goal: maximize measured fitness. The client sends Gemini a fixed, plain-language description of that goal and of three reward weights. It sends no sequence, measurement, hidden label, API key in the prompt, run record or executable tool. Gemini proposes three numbers: the uncertainty penalty, distance penalty and diversity bonus. Ordinary code builds the full reward specification, fixes the mutation and budget constraints, and validates the result with the existing allowlist and numeric bounds. Any extra field, duplicate key, non-finite number or out-of-range weight is rejected. An invalid model response is retried once; after two invalid responses, or a service/configuration failure, the recorded rule-based default is used. Transport errors do not trigger automatic repeated calls.

The request asks for structured JSON using the Gemini API; its [structured-output documentation](https://ai.google.dev/gemini-api/docs/structured-output) describes the format. A structured response still requires application-side validation: conforming to a shape does not prove that weights are useful. The client uses a fixed Google endpoint, puts the key in a request header and records only sanitized status and token counts. Configuration comes from `GEMINI_API_KEY` and `GEMINI_MODEL` in the process environment or the ignored `backend/.env`, with process variables taking precedence. The tested `python-dotenv` 1.2.3 release is pinned for this workflow; its [maintainer documentation](https://github.com/theskumar/python-dotenv) explains `dotenv_values`, which reads without changing the process environment.

The saved record contains the validated specification and can be replayed without another model call. Temperature zero does not guarantee a hosted model will return identical results in a later request. The compiler does not yet accept arbitrary natural-language goals, choose repairs, give the model warning evidence, or run without the rule-based validator. It does not claim that the model's choices are better than the illustrative defaults.

### Live development check

The configured `gemini-3.5-flash-lite` model returned an accepted response on the first request: weights 0.5 for uncertainty, 0.5 for distance and 0.2 for diversity. The API reported 39 input tokens and 39 output tokens, 78 total. The saved decision record is [result.json](../../output/gemini_goal_check/result.json). It contains no credential. One call does not establish reliability across requests, account availability or cost; pricing and quota depend on the account and provider.

The saved result then supplied the specification for a seed-13 amylase pilot. Ten batches used 100 additional measurements. The ranges covered 95/100 selected scores, and the best score among the 200 known variants was 0.18225. This is an exploratory single run, not evidence of an advantage or a coverage guarantee. An independent audit checked the compiled-file fingerprint, pre-reveal ordering, all candidate distances and sequential rewards, source measurements and budget. The record and audit are in [the pilot output](../../output/amylase_gemini_pilot_seed13). The backend suite passed 41 tests, including invalid output, retry, fallback, fixed constraints and request construction.

To repeat from the project root after installing the research requirements, with a new output path for each step:

```sh
PYTHONPATH=backend:. python3 -m scripts.amylase.compile_reward_goal output/my-gemini-spec.json
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend:. python3 -m scripts.amylase.run_reward_pilot output/my-gemini-pilot output/my-gemini-spec.json --seed 13
```

The first command makes a hosted request and may consume quota or incur charges. A fallback is explicitly marked in the result and its pilot record; it must not be counted as a successful model proposal. The second command consumes the saved result and does not call Gemini.

### Remaining work

The synopsis also calls for checked warning-driven repair proposals, repair ordering, meaningful verification, rollback, abstention, a no-LLM comparison and a fair evaluation. None is demonstrated by this check. The model output is only a proposal, and its numeric weights are not scientifically calibrated.

## Natural-language goals

The goal compiler now accepts an optional short user description of a protein fitness search. Gemini receives the text as part of a request and proposes the three permitted reward weights. The application constructs and validates the specification locally: the objective remains `maximize_fitness`, and the existing mutation limit, budget, allowed weight ranges and stopping limit cannot be changed by the model. No protein sequence or measured score is sent by the compiler unless the user includes it in their own text. The goal text is saved in the output record, so do not include secrets or material you do not want sent to the provider and stored locally.

The model is instructed to flag unsupported objectives, changes to constraints or budgets, and unrelated requests. A flagged goal is rejected; invalid output is retried once, while service or configuration errors stop the command. Unlike the original fixed-goal mode, this path does not fall back to a generic specification. **The model can still misunderstand a request or misclassify it as supported.** Inspect the saved specification and verify that its fixed limits and weights reflect the intended task before using it. The validator checks the structure and bounds; it cannot prove that the model interpreted the words correctly or that the proposed weights are effective. Google's [structured-output documentation](https://ai.google.dev/gemini-api/docs/structured-output) likewise requires application validation and handling semantically incorrect results.

From the repository root, using a new path for each output:

```sh
PYTHONPATH=backend:. python3 -m scripts.amylase.compile_reward_goal output/my-goal.json --goal 'Maximize protein fitness while favoring diverse batches.'
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend:. python3 -m scripts.amylase.run_reward_pilot output/my-run output/my-goal.json --dataset amylase --seed 13 --repair --targeted-disagreement --direct-diversity
```

The first command uses `GEMINI_API_KEY` and `GEMINI_MODEL` from the environment or ignored `backend/.env`, sends a provider request, and may incur charges. The second uses the saved specification; it makes no Gemini repair calls unless `--gemini-repair` is explicitly selected. Omitting `--goal` preserves the previous fixed-goal behavior and its documented fallback. A user goal that changes hard limits or asks for a different objective is outside the current supported domain.

### Verification

A live request for fitness maximization with diversity produced the saved [validated specification](../../output/natural_goal_check.json), with 141 provider-reported tokens. The saved file was used in a real Amylase run with rule-based repair; it stopped after two failed repair actions and 20 new measurements. A separate check recomputed the run summary against the source scores, checked the input fingerprint and confirmed 20/20 recorded intervals covered their associated scores. This is a functional check of one run, not an independent model benchmark, repair benefit or coverage guarantee. A separate live request for fitness minimization was rejected as unsupported; its token usage and actual billing were not captured.

Four focused tests cover validated output, fixed limits, unsupported and unavailable responses, malformed or duplicated fields, goal length, request construction and passing the saved goal into the pilot. All 150 backend tests passed. Hosted-model responses can change; the live checks do not prove reliable classification for every natural-language request.

### Local web workflow

The local workspace provides a Goals page to compile and review a short goal before selecting it on the Experiments page. The full goal text is sent to Gemini and saved under `output/web_goals/`; requests may incur charges. The backend rejects a saved file whose fingerprint changed since it was selected, validates the three bounded weights and the fixed constraints, and records the goal and specification in the run. This prevents accidental use of a changed file, not semantic mistakes by Gemini. A live web flow compiled a sample goal with one accepted provider request and 138 reported tokens, displayed its weights, used the saved specification in an Amylase run, and retained it in the run review. This is an engineering check, not a validated interpretation or proof of fitness improvement.
