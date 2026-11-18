<div align="center">

# Repeated matched amylase development comparison

Protocol and findings

</div>

## Protocol

Recorded before the runs on 16 November 2026. This is an exploratory development comparison on one protein, not the final IRED or hydrophobic-core evaluation. Existing development observations, including seed 13, informed the settings below and are not independent confirmation.

### Runs and information boundaries

Attempt all initial-set seeds 21 through 30, with nine methods per seed: random, greedy prediction, the fixed example reward, rule-based repair, Gemini-assisted repair, mean-plus-spread, expected improvement, finite-pool recombination and AdaLead-style local search. Every method receives the same 100 initial measurements, eligible pool, four-substitution limit, batches of at most ten and maximum 100 new measurements. Random uses selection seed `1000 + initial seed`. Every model-based method uses range-setting role seed `2000 + initial seed` and model-member seed `3000 + initial seed`.

The fixed, rule-based and Gemini-assisted repair methods start from the checked-in [example reward specification](../../../configs/reward_spec_example.json). The two repair methods differ in option ordering: rule-based tries cheapest first; Gemini may prioritize one permitted option, and every option still undergoes the same verifier. A missing or invalid model response is recorded as a fallback, not counted as a successful model choice. Record model, sanitized choice, token usage if returned, failure status and actual runtime. The Gemini method sends only warning type and allowed option metadata; it does not receive candidate sequences or scores.

Each selector sees only the supported measurement interface. Record full pre-reveal evidence and every actual stop. Generate all method records before the separate evaluator loads all eligible pool scores. The evaluator verifies source fingerprints, initial measurements, selections, reveal chronology, uniqueness, budget and terminal state, then reports best observed score including the initial examples, finite-pool regret, top-1% status, actual new measurements, stop reason, and available prediction-range coverage and width. Do not pad early-stopped runs or treat absent prediction ranges as zero coverage. Preserve complete records losslessly with compressed and uncompressed fingerprints.

### Reporting and checks

Report all requested seed-method pairs, including errors, incomplete runs, early stops and Gemini fallback counts; never silently substitute another seed. Match initial IDs, role sets, representation fingerprints and shared predictor settings within each seed. Independently reconstruct all selections and outcome summaries from the records and source measurements; for warning, repair, local-search and acquisition evidence, check representative cases and report the scope rather than claiming a complete independent audit unless one was actually performed. Record code and source fingerprints and ensure no credential is written to logs.

Summarize per-method distributions across seeds and paired differences between rule-based repair and the fixed reward, including actual query counts and stops. These ten runs share one protein and overlapping candidate pools: they are not independent biological datasets, and no statistical significance or general superiority is implied. The eligible pool optimum is an evaluator-only reference, not a biological global optimum. Conformal coverage is not guaranteed under adaptive selection. Model-call availability and charges depend on the account; retain both model-backed and fallback cases in the report. The need to examine run-to-run variation rather than rely on a single seed is discussed by [Bouthillier et al.](https://proceedings.mlr.press/v97/bouthillier19a.html).

## Findings

Completed 16 November 2026 under the [predeclared protocol](repeated_matched.md#protocol). All 90 planned runs completed: nine methods for each of ten initial seeds. These runs share one protein, one finite measured pool and overlapping observations. They are development evidence, not ten independent biological datasets or a final evaluation on IRED or the three hydrophobic-core proteins.

### What happened

Each method started with the same 100 measurements for a given seed and could request at most 100 more. The table reports the median across ten runs of each method's best score at its actual stop. The recombination and AdaLead-style methods are the finite-pool adaptations described in [their protocol](local_search_baselines.md#protocol).

| Method | Median best score | New measurements per run | Stop behavior |
| --- | ---: | ---: | --- |
| Random | 0.19711 | 100 | Budget exhausted in all 10 |
| Greedy prediction | 0.19332 | 100 | Budget exhausted in all 10 |
| Fixed reward | 0.19332 | 100 | Budget exhausted in all 10 |
| Rule-based repair | 0.19332 | 20 | Two failed repairs in all 10 |
| Gemini-assisted repair | 0.19332 | 20 | Two failed repairs in all 10 |
| Mean plus model spread | 0.19332 | 100 | Budget exhausted in all 10 |
| Gaussian expected improvement | 0.19332 | 100 | Budget exhausted in all 10 |
| Recombination and mutation | 0.21163 | 100 | Budget exhausted in all 10 |
| AdaLead-style local search | 0.19332 | 0–32 | No eligible neighbors in all 10 |

The fixed-reward and rule-based repair runs ended with identical best scores for every matched seed, although the fixed method used 100 new measurements and repair stopped after 20. The Gemini-assisted and rule-based repair runs also had equal final best scores for every seed. This does not prove the methods equivalent: the current repair rule never accepted a change in these runs. Recombination reached the highest recorded score in the eligible pool in 8 of 10 runs; that finite-pool outcome does not establish broad superiority.

Every initial set already included a candidate in the eligible pool's top 1%, so the top-1% measure cannot distinguish methods here. The eligible-pool maximum is 0.21163; it is an evaluator-only reference, not a global biological optimum. AdaLead-style search had no permitted initial neighbor in two seeds, and its median new-measurement count was four. No early-stopped run was padded to 100 queries.

### Warnings, ranges and model calls

Both repair modes encountered two disagreement warnings per seed. Every one of their 120 proposed weight changes failed the requirement to displace **all** flagged batch members on replay; the other three implemented verification checks passed in those attempts. Thus the original reward was retained and the system stopped. A disagreement warning is not an independently verified prediction failure, and the strict all-members rule is provisional. The results identify a concrete development problem; they do not justify silently weakening the rule after seeing these runs.

Across the selected measurements, saved prediction ranges covered 922/1,000 for greedy, 818/1,000 for fixed reward, 142/200 for each repair mode, 909/1,000 for mean-plus-spread, 935/1,000 for expected improvement, 804/1,000 for recombination and 40/76 for AdaLead-style search. Random sampling did not calculate ranges. The differing denominators, early stopping and adaptive selection make these descriptive counts rather than comparable guarantees. Mean range widths are retained per run; their per-method medians are in [method_summary.csv](../../../output/amylase/search/amylase_repeated_matched_21_30/method_summary.csv).

Gemini returned valid menu choices for 20 requests, with no recorded fallback. It chose option 1 seventeen times and option 0 three times. The service reported 2,800 input and 184 output tokens, 2,984 total; actual charges depend on the account. It received warning types and option metadata only, not sequences or fitness scores. No model-chosen proposal passed the verifier, so this experiment does not establish that model advice helps.

### Verification and evidence

The independent audit checked all 90 records, initial sets, fitting and member-seed assignments, source fingerprints and revealed scores, 658 selection batches, best-score curves, final summary metrics, budget accounting and stop reasons. It reconstructed all acquisition scores and rankings, all reward selections and 120 repair replays. It separately reconstructed local proposal sets for 27 rounds in seeds 21 and 30, and candidate distances for six representative first rounds; these two checks were **not** independently repeated for every seed. A second audit checked model-advice and token accounting against the records. The configured credential was not found in the audited run records. The full backend suite passed 77 tests before the runs.

Complete per-run records, stop statuses, fingerprints, curves, per-run summary, paired differences and both audit reports are in [the output directory](../../../output/amylase/search/amylase_repeated_matched_21_30). No final test-set conclusion should be drawn until the development choices, evaluation procedure and evidence boundaries are frozen and then applied to the other proteins. In particular, the frequently triggered disagreement warning, strict replay requirement, reuse of calibration examples and in-sample ranking check remain substantial limitations.

To repeat the predeclared development run with a new directory:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend:. python3 -m scripts.multiprotein.repeated_matched output/my-repeated-comparison
```

The command can make Gemini requests and may incur charges. `--resume` preserves completed, failed and interrupted statuses and refuses changed source code or inputs; it does not silently rerun an interrupted method. The independent audit accepts a new report path via `--report` and refuses to overwrite an existing report.
