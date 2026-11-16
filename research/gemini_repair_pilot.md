# Gemini-assisted repair: first development run

Completed 16 November 2026. This is a single operational check of a restricted model-assisted repair choice; it is not evidence that Gemini improves the search or that any repair succeeds.

## What Gemini can choose

The rule-based repair system builds the same finite, locally validated menu as before. For each triggered warning with targets, Gemini receives the warning type and a numbered list containing only each option's allowed term, proposed weight and cost. It receives no protein sequences, measured scores, hidden labels or model predictions. It chooses a number; it cannot add a parameter, write code, change hard constraints or apply a repair. Google recommends validating structured output in application code even when the response follows a schema ([Gemini structured-output documentation](https://ai.google.dev/gemini-api/docs/structured-output)).

The chosen option is tried first. If it fails the existing verifier, remaining options are tried in increasing cost order. Invalid choices are retried once; a service failure or two invalid choices falls back to the original cheapest-first ordering. Each decision records its sanitized option list, selected number, source, attempt status and available token counts. Every actual proposal is independently checked by the same verifier as the rule-based system.

This policy resolves a conflict in the synopsis for development: it asks both for cheapest-first repair and an LLM-chosen repair. The rule-based comparator remains cheapest-first; the model-assisted version tries the model's choice first. Consequently the two methods can differ in which passing repair they accept, and this distinction must be disclosed in comparisons. The model sees only warning type and menu metadata, not the underlying evidence, limiting what its choice can meaningfully contribute.

## What happened in the pilot

Using the same initial seed, previously saved Gemini-generated starting specification and budget as the [rule-based repair pilot](repair_pilot_findings.md), the model selected option 1, the middle-cost option, for each of two disagreement warnings. Both model requests returned valid choices; each reported 140 input tokens and 10 output tokens. For each warning the system then checked weights 1.0, 0.75 and 1.5 in that order. All failed the requirement to displace every flagged batch member. The old rule was retained twice and the run stopped after 20 new measurements, leaving 80 unspent.

The same three proposals had already failed in the independently audited rule-based run. A separate audit matched the initial measurements, both selected batches and each proposal's verification results against that run, checked the model option metadata and stop, and confirmed the local key was absent from the run record. All 55 backend tests passed, including invalid choices, retries, fallback, option sanitization and verification after a model preference. The compressed record and audit are in [the pilot output](../output/amylase_gemini_repair_pilot_seed13/).

The two runs use the same starting examples and candidate setup but are a single development comparison. They do not establish model reliability, scientific effectiveness, generalization, or the value of the warning. No repair was accepted in either run. The model-generated starting weights were reused from an earlier saved response; the two subsequent calls were only for repair choices.

To reproduce with a new output directory and the pinned representations:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend python3 scripts/run_reward_pilot.py output/my-gemini-repair output/gemini_goal_check/result.json --seed 13 --gemini-repair
```

This command calls Gemini when eligible warnings arise and may consume quota or incur charges. Hosted responses can vary. Without `--gemini-repair`, `--repair` uses the rule-based ordering and makes no Gemini repair calls. Saved decisions and results identify fallback separately, so fallback is not counted as successful model advice.
