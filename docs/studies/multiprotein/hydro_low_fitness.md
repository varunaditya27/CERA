<div align="center">

# Hydro low-fitness start

Protocol, runbook and findings

</div>

## Protocol

### Question and limitation

How do the nine existing methods behave when their 100 initial measured examples are sampled from the eligible training side of the Hydro low-to-high fitness split, while every eligible unmeasured variant remains available for later selection? This extends the score-blind candidate-access choice used in the IRED low-change-start study to the other proposed shift type. It is a retrospective stress test, not an official FLIP2 evaluation or a realistic procedure for obtaining a low-fitness starting set without prior knowledge: [FLIP2](https://flip.protein.properties/) defines these groups using fitness scores. Starting-pool membership therefore conveys privileged outcome information. The predictor receives no unseen score, and later candidates are not filtered by split. Their measured scores become available only after selection.

This plan was written after earlier searches and static held-out predictions were inspected, so results are exploratory and not independent confirmation. The aim is to document actual behavior, not tune on test outcomes. The static held-out results cannot be interpreted as showing what will happen during sequential retraining. The protein-engineering [uncertainty benchmark](https://pmc.ncbi.nlm.nih.gov/articles/PMC11741572/) separately studies iterative acquisition and prediction metrics, reinforcing the need to measure each behavior directly.

### Fixed design

Use each Hydro protein separately, initial seeds 141–150, all nine existing methods in their prior order, 100 sampled training-side measurements, a maximum of 100 new measurements, batches of ten and the existing four-substitution cap. Include benchmark validation-flagged training rows, as in the existing study; 20 of the initial 100 are independently reserved to set prediction intervals. Use the existing reward specification, predictor, repair checks and stopping rules. The Gemini-assisted arm may make paid provider calls; exact charges and quota are unknown. Methods receive the same starting examples for each protein and seed. Initial training-side pool sizes are 263, 713 and 701 for P06241, P01053 and P0A9X9 respectively, subject to verification against pinned source fingerprints before execution.

After all configured runs have terminal status, verify and report actual selection counts, methods stopped early, prediction-range coverage, repair actions, Gemini attempts and matched differences against fixed reward. Count how many selected variants came from each benchmark split only after selection, with a separate final evaluator; the selector must not receive split labels. Pool optimum and top-1% outcomes use all eligible variants, not just the higher-fitness side. Do not pool score values across proteins. A search that selects from the training side remains valid for this design, but must not be described as a test-only shift experiment.

### Implementation and verification gates

1. Permit the privileged starting pool only under an explicit Hydro-specific runner flag. Keep the default and existing IRED scope intact. The manifest, independent audit and final evaluator must identify this separate study and reject mixed or mismatched settings.
2. Test initial sampling and all-eligible candidate access with synthetic data. Test malformed manifests, missing groups and changed settings; preserve all historical study verification. No selector or repair function may receive unseen scores or split labels.
3. Run the backend suite and commit implementation and this protocol before real runs. Record a manifest, data, reference, code and representation fingerprints. Preserve failures and interrupted records; do not silently rerun or erase them.
4. For each completed run independently reconstruct initial observations, selection decisions, reveals, repair checks, record fingerprints and actual budgets; then evaluate using source scores and record selected split membership. This audit does not independently refit all predictors or establish biological detector accuracy.

Coverage under this shifted, adaptive sampling need not have a formal 90% guarantee. Early stopping changes how many measurements are available for comparisons and recovery. The ten seeds reuse each fixed protein dataset and are not independent biological replications. No evidence from this post-result study should be presented as a prespecified causal claim or as proof that a target has been met.

## Runbook

The [protocol](hydro_low_fitness.md#protocol) defines the privileged score-derived starting pool and unrestricted later candidate pool. All nine methods are planned for each of three proteins and ten matched seeds. The Gemini arm may incur provider charges; actual billing is not captured by the run records.

For each `PROTEIN` in `P06241`, `P01053` and `P0A9X9`, use the following command with `PROTEIN` replaced literally. Each output directory must be new.

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend:. python3 -m scripts.multiprotein.run_matched_proteins output/hydro_low_fitness_PROTEIN_141_150 --dataset hydro-PROTEIN --initial-pool train --hydro-low-fitness --seeds 141 142 143 144 145 146 147 148 149 150 --methods random greedy fixed repair gemini_repair ucb ei genetic adalead --specification configs/reward_spec_example.json --targeted-disagreement --direct-diversity
```

After all 270 statuses are terminal, use all three roots in both commands. `--resume` checks exact manifest and completed-record fingerprints; interrupted and failed runs are preserved and are not silently replaced.

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend:. python3 -m scripts.multiprotein.audit_matched_proteins output/hydro_low_fitness_P06241_141_150 output/hydro_low_fitness_P01053_141_150 output/hydro_low_fitness_P0A9X9_141_150 --hydro-low-fitness
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend:. python3 -m scripts.multiprotein.evaluate_matched_proteins output/hydro_low_fitness_141_150_report.json output/hydro_low_fitness_P06241_141_150 output/hydro_low_fitness_P01053_141_150 output/hydro_low_fitness_P0A9X9_141_150 --specification configs/reward_spec_example.json --hydro-low-fitness
```

The special scopes require exactly the three Hydro groups, all methods, the specified seeds, both repair checks, the pinned specification and matching code and software versions. The audit checks initial scores and subsequent selections and reveals, and the evaluator records the later selections' split membership. The model receives split-free candidates and only revealed scores. The audit does not refit all predictors or establish biological warning validity.

## Findings

All 270 planned runs completed: three Hydro proteins, ten matched starts and nine methods. The [protocol](hydro_low_fitness.md#protocol) sampled 100 starting measurements from FLIP2's lower-fitness training side and then allowed every eligible unmeasured variant to be selected. This is an **exploratory retrospective stress test**. The starting group is defined using measured fitness, so its membership is privileged information that would not normally be available before measurement. Later selectors were given candidate sequences and revealed measurements, not unseen scores or split labels. Earlier study results had already been inspected, and this is not an independent confirmatory experiment or an official FLIP2 benchmark score.

### Repair compared with fixed reward

Each cell below compares the best measured score when each policy actually stopped. The two repair policies had the same best-score outcomes in every pair; fixed reward always used all 100 new measurements. A tie is an absolute score difference at most 1e-12.

| Protein | Repair higher / tied / lower than fixed | Repair median new measurements (range) | Repair stops after failed repairs | Fixed range coverage | Repair range coverage |
| --- | --- | --- | ---: | ---: | ---: |
| P06241 | 0 / 0 / 10 | 30 (20–40) | 10 of 10 | 472 / 1,000 | 87 / 290 |
| P01053 | 0 / 1 / 9 | 30 (20–50) | 10 of 10 | 428 / 1,000 | 122 / 330 |
| P0A9X9 | 0 / 4 / 6 | 30 (20–100) | 7 of 10 | 759 / 1,000 | 341 / 510 |

The Gemini-assisted arm has the same counts in this table as the rule-based arm. Across the three proteins, each repair policy stopped after failed repairs in 27 of 30 runs and used 1,130 new measurements, versus 3,000 for fixed reward. Each accepted three repairs: one on P06241, two on P01053 and none on P0A9X9. An accepted repair passed the implemented local checks; it is not proof of future improvement.

As a **post-result** comparison, fixed reward's recorded best score at the same measurement count as the repair policy's stop tied the repair policy in all 30 matched starts for each repair arm. This checks best observed score at that point, not whether the policies selected the same variants, whether their later outcomes would match, or whether they are equivalent. In the final comparison above, fixed reward could continue measuring after repair stopped. Neither comparison isolates the effect of a repair from the effect of stopping.

The range counts include all new measurements in a run, including those before and after any repair. They do not establish after-repair coverage or a coverage guarantee; runs and measurements are dependent, and the groups are selected by fitness. The [full report](../../../output/hydro_low_fitness_141_150_report.json) retains each start, curve, range width, warning, repair and recovery status. In particular, a run that stopped before 30 later measurements is recorded as having insufficient follow-up, not as recovered or not recovered.

### Candidate access and other methods

The repair policy selected 252 of 290 P06241 variants, 279 of 330 P01053 variants, and 483 of 510 P0A9X9 variants from the benchmark's test side; the Gemini-assisted policy had the same split counts. Remaining selections came from the training side. These counts were calculated afterward and show that the search was **not restricted** to either side. Fixed reward selected 958/1,000, 889/1,000 and 972/1,000 from the test side respectively. Split membership is score-derived, so these counts must not be interpreted as a realistic mechanism for identifying high-fitness candidates in advance.

The [summary](../../../output/hydro_low_fitness_141_150_summary.json) provides all nine methods' median best scores, actual measurement ranges, stopping reasons, selected split counts and paired differences. Scores use different scales across proteins. Finite-pool genetic and AdaLead-style methods remain adaptations to the measured pool. AdaLead-style search stopped for lack of permitted neighbors in all ten P06241 runs, all ten P01053 runs and six P0A9X9 runs; its remaining four P0A9X9 runs used the budget. Random search has no prediction intervals.

### Gemini requests

Across 30 Gemini-assisted runs, records show 61 advice attempts: 60 valid Gemini selections and one fallback after an HTTP 503 response. The records report 8,953 total tokens. Reported tokens are provider metadata available to the client, not verified billing; requests that fail before usage metadata may be absent from the total. Actual charges and quota were not checked. Matching final scores do not prove the language model made identical choices or could never affect other runs.

### Verification and remaining work

The [decision audit](../../../output/hydro_low_fitness_141_150_audit.json) checked 270 completed records, 2,191 selection batches and 363 repair replays, plus one representative distance calculation and two local-proposal rounds per protein. The [outcome audit](../../../output/hydro_low_fitness_141_150_summary_audit.json) independently checked 21,747 measurements, source scores, split counts, range coverage, stopping and best-score curves against the compressed records; it rejected a deliberately altered outcome. These audits do not independently refit every predictor or establish the biological validity of warnings. The ten starts reuse each fixed protein dataset and do not constitute ten independent biological experiments.

This study does not complete the proposed official test-only split search, independently validate detector accuracy, test later rollback of an accepted reward, or prove a causal repair effect. The broader [completion evidence review](../../overview/completion_review.md) tracks those and the final deliverables.
