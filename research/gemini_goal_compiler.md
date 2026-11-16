# Gemini reward-weight compilation

Implemented and checked 16 November 2026. This is a constrained first version of the language-model component, not the complete LLM-assisted repair system.

## What the model can do

The current project has one supported goal: maximize measured fitness. The client sends Gemini a fixed, plain-language description of that goal and of three reward weights. It sends no sequence, measurement, hidden label, API key in the prompt, run record or executable tool. Gemini proposes three numbers: the uncertainty penalty, distance penalty and diversity bonus. Ordinary code builds the full reward specification, fixes the mutation and budget constraints, and validates the result with the existing allowlist and numeric bounds. Any extra field, duplicate key, non-finite number or out-of-range weight is rejected. An invalid model response is retried once; after two invalid responses, or a service/configuration failure, the recorded rule-based default is used. Transport errors do not trigger automatic repeated calls.

The request asks for structured JSON using the Gemini API; its [structured-output documentation](https://ai.google.dev/gemini-api/docs/structured-output) describes the format. A structured response still requires application-side validation: conforming to a shape does not prove that weights are useful. The client uses a fixed Google endpoint, puts the key in a request header and records only sanitized status and token counts. Configuration comes from `GEMINI_API_KEY` and `GEMINI_MODEL` in the process environment or the ignored `backend/.env`, with process variables taking precedence. The tested `python-dotenv` 1.2.3 release is pinned for this workflow; its [maintainer documentation](https://github.com/theskumar/python-dotenv) explains `dotenv_values`, which reads without changing the process environment.

The saved record contains the validated specification and can be replayed without another model call. Temperature zero does not guarantee a hosted model will return identical results in a later request. The compiler does not yet accept arbitrary natural-language goals, choose repairs, give the model warning evidence, or run without the rule-based validator. It does not claim that the model's choices are better than the illustrative defaults.

## Live development check

The configured `gemini-3.5-flash-lite` model returned an accepted response on the first request: weights 0.5 for uncertainty, 0.5 for distance and 0.2 for diversity. The API reported 39 input tokens and 39 output tokens, 78 total. The saved decision record is [result.json](../output/gemini_goal_check/result.json). It contains no credential. One call does not establish reliability across requests, account availability or cost; pricing and quota depend on the account and provider.

The saved result then supplied the specification for a seed-13 amylase pilot. Ten batches used 100 additional measurements. The ranges covered 95/100 selected scores, and the best score among the 200 known variants was 0.18225. This is an exploratory single run, not evidence of an advantage or a coverage guarantee. An independent audit checked the compiled-file fingerprint, pre-reveal ordering, all candidate distances and sequential rewards, source measurements and budget. The record and audit are in [the pilot output](../output/amylase_gemini_pilot_seed13/). The backend suite passed 41 tests, including invalid output, retry, fallback, fixed constraints and request construction.

To repeat from the project root after installing the research requirements, with a new output path for each step:

```sh
PYTHONPATH=backend python3 scripts/compile_reward_goal.py output/my-gemini-spec.json
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend python3 scripts/run_reward_pilot.py output/my-gemini-pilot output/my-gemini-spec.json --seed 13
```

The first command makes a hosted request and may consume quota or incur charges. A fallback is explicitly marked in the result and its pilot record; it must not be counted as a successful model proposal. The second command consumes the saved result and does not call Gemini.

## Remaining work

The synopsis also calls for checked warning-driven repair proposals, repair ordering, meaningful verification, rollback, abstention, a no-LLM comparison and a fair evaluation. None is demonstrated by this check. The model output is only a proposal, and its numeric weights are not scientifically calibrated.
