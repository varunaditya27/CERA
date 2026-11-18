<div align="center">

# Evaluation readiness review

Review notes

</div>

This review was made on 16 November 2026 from the repository's current code, recorded development results and the earlier [research roadmap](roadmap.md). It is not a claim that the submitted project is complete.

## What exists

- Controlled retrospective searches, saved measurement records, five model predictors, prediction ranges, warning rules, constrained repairs, a rule-based repair selector and an optional Gemini menu advisor are implemented. Their development behavior and limitations are recorded in the [work log](../history/work_log.md).
- Amylase has multiple matched development comparisons. The most recent two comparisons have a reusable audit, which reconstructs choices using saved model predictions and distances; it does not independently refit the predictors or validate every scientific assumption.
- IRED and each of the three hydrophobic-core proteins have verified sequence representation caches and runner dispatch. No matched evaluation results on those proteins are recorded. The IRED local file represents a subset of the screened variants; hydrophobic-core initial training membership is derived from measured scores in the original benchmark split. See [IRED](../data/ired_preparation.md) and [hydrophobic-core](../data/hydro_preparation.md) preparation.

## Important gaps before a final claim

1. **Define what successful recovery means.** The roadmap calls for a failure start, observation window, minimum follow-up and treatment of runs that stop without recovery. No frozen, independently evaluated recovery metric is recorded. A warning, an accepted repair and improved later outcomes are different events.
2. **Establish what the repair checks prove.** The direct diversity check has a controlled example and saved-batch replays, but no accepted repair occurred in its new five-seed comparison. For coverage, a reward weight does not itself change the model's already computed ranges, and the calibration examples are reused. A passing check is not evidence that later coverage improved.
3. **Freeze the comparisons.** The existing development comparison includes random, greedy, fixed reward, rule-based and Gemini-assisted repairs, two uncertainty-based acquisitions and finite-pool local searches. Their limitations are documented, but the precise final set, primary outcome, repair mode and reporting plan still need a frozen protocol. An expected-improvement acquisition is not by itself a full independently implemented Bayesian-optimization framework.
4. **Evaluate the intended proteins separately.** No multi-seed IRED or hydrophobic-core search comparisons are recorded. Each hydrophobic-core protein has a different sequence and score scale, so pooling raw scores would be misleading. The score-derived starting split must remain visible as a limitation.
5. **Complete reproducible reporting.** Warning rates need an independently defined event and denominator; costs, early stops, unrecovered cases and failed runs must remain visible. The roadmap also calls for component-removal comparisons and a reader-reproducible report. The current user interface is a dataset catalog, not an experiment dashboard.

## Why freeze before using evaluation results

Repeatedly changing a method after seeing its evaluation results can make the evaluation look more favorable without demonstrating improvement on new examples. This is a known issue in adaptive analysis; see [Dwork et al. (2015)](https://papers.neurips.cc/paper_files/paper/2015/hash/bad5f33780c42f2588878a9d07405083-Abstract.html). This does not make the available datasets magically independent: their labels are local files and some source-level score checks were already performed. It means future method choices and outcome access must be recorded honestly.

## Candidate next step

Define and review a recovery measurement using saved amylase development records, including examples where there is insufficient follow-up or an early stop. Separately specify the minimum later evidence required to evaluate a repair. A development definition would still need to be frozen before new protein outcomes are used to assess it. This is a proposal, not a settled metric or an authorization to implement code.
