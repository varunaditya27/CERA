# Hydro low-fitness-start search findings

All 270 planned runs completed: three Hydro proteins, ten matched starts and nine methods. The [protocol](hydro_low_fitness_search_protocol.md) sampled 100 starting measurements from FLIP2's lower-fitness training side and then allowed every eligible unmeasured variant to be selected. This is an **exploratory retrospective stress test**. The starting group is defined using measured fitness, so its membership is privileged information that would not normally be available before measurement. Later selectors were given candidate sequences and revealed measurements, not unseen scores or split labels. Earlier study results had already been inspected, and this is not an independent confirmatory experiment or an official FLIP2 benchmark score.

## Repair compared with fixed reward

Each cell below compares the best measured score when each policy actually stopped. The two repair policies had the same best-score outcomes in every pair; fixed reward always used all 100 new measurements. A tie is an absolute score difference at most 1e-12.

| Protein | Repair higher / tied / lower than fixed | Repair median new measurements (range) | Repair stops after failed repairs | Fixed range coverage | Repair range coverage |
| --- | --- | --- | ---: | ---: | ---: |
| P06241 | 0 / 0 / 10 | 30 (20–40) | 10 of 10 | 472 / 1,000 | 87 / 290 |
| P01053 | 0 / 1 / 9 | 30 (20–50) | 10 of 10 | 428 / 1,000 | 122 / 330 |
| P0A9X9 | 0 / 4 / 6 | 30 (20–100) | 7 of 10 | 759 / 1,000 | 341 / 510 |

The Gemini-assisted arm has the same counts in this table as the rule-based arm. Across the three proteins, each repair policy stopped after failed repairs in 27 of 30 runs and used 1,130 new measurements, versus 3,000 for fixed reward. Each accepted three repairs: one on P06241, two on P01053 and none on P0A9X9. An accepted repair passed the implemented local checks; it is not proof of future improvement.

As a **post-result** comparison, fixed reward's recorded best score at the same measurement count as the repair policy's stop tied the repair policy in all 30 matched starts for each repair arm. This checks best observed score at that point, not whether the policies selected the same variants, whether their later outcomes would match, or whether they are equivalent. In the final comparison above, fixed reward could continue measuring after repair stopped. Neither comparison isolates the effect of a repair from the effect of stopping.

The range counts include all new measurements in a run, including those before and after any repair. They do not establish after-repair coverage or a coverage guarantee; runs and measurements are dependent, and the groups are selected by fitness. The [full report](../output/hydro_low_fitness_141_150_report.json) retains each start, curve, range width, warning, repair and recovery status. In particular, a run that stopped before 30 later measurements is recorded as having insufficient follow-up, not as recovered or not recovered.

## Candidate access and other methods

The repair policy selected 252 of 290 P06241 variants, 279 of 330 P01053 variants, and 483 of 510 P0A9X9 variants from the benchmark's test side; the Gemini-assisted policy had the same split counts. Remaining selections came from the training side. These counts were calculated afterward and show that the search was **not restricted** to either side. Fixed reward selected 958/1,000, 889/1,000 and 972/1,000 from the test side respectively. Split membership is score-derived, so these counts must not be interpreted as a realistic mechanism for identifying high-fitness candidates in advance.

The [summary](../output/hydro_low_fitness_141_150_summary.json) provides all nine methods' median best scores, actual measurement ranges, stopping reasons, selected split counts and paired differences. Scores use different scales across proteins. Finite-pool genetic and AdaLead-style methods remain adaptations to the measured pool. AdaLead-style search stopped for lack of permitted neighbors in all ten P06241 runs, all ten P01053 runs and six P0A9X9 runs; its remaining four P0A9X9 runs used the budget. Random search has no prediction intervals.

## Gemini requests

Across 30 Gemini-assisted runs, records show 61 advice attempts: 60 valid Gemini selections and one fallback after an HTTP 503 response. The records report 8,953 total tokens. Reported tokens are provider metadata available to the client, not verified billing; requests that fail before usage metadata may be absent from the total. Actual charges and quota were not checked. Matching final scores do not prove the language model made identical choices or could never affect other runs.

## Verification and remaining work

The [decision audit](../output/hydro_low_fitness_141_150_audit.json) checked 270 completed records, 2,191 selection batches and 363 repair replays, plus one representative distance calculation and two local-proposal rounds per protein. The [outcome audit](../output/hydro_low_fitness_141_150_summary_audit.json) independently checked 21,747 measurements, source scores, split counts, range coverage, stopping and best-score curves against the compressed records; it rejected a deliberately altered outcome. These audits do not independently refit every predictor or establish the biological validity of warnings. The ten starts reuse each fixed protein dataset and do not constitute ten independent biological experiments.

This study does not complete the proposed official test-only split search, independently validate detector accuracy, test later rollback of an accepted reward, or prove a causal repair effect. The broader [completion evidence review](completion_evidence_review.md) tracks those and the final deliverables.
