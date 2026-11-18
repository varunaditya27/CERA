<div align="center">

# Reward repair and early stopping in retrospective protein fitness search

Draft

</div>

Workshop draft for project-guide review

## Abstract

We evaluated two policies that change a learned scoring rule after a warning in a retrospective search over previously measured protein variants. In a 360-run comparison across four protein groups, each repair policy tied a fixed scoring rule in 35 of 40 matched starts and scored lower in five at its actual stopping point. Comparing at the repair policy's measurement count changed four losses to ties, leaving one lower score and 39 ties for each policy. These findings show why a comparison of adaptive policies should report both the outcomes and the number of measurements each policy used.

## Motivation and evaluation

A learned reward is a scoring rule that uses predictions to choose what to measure. Evidence that optimizing an imperfect proxy can depart from reference performance motivates tracking the measured scores separately. The FLIP2 benchmark also distinguishes different kinds of changes between starting and test examples. Our analysis asks whether the tested repair policies improved final best scores within fixed, previously measured candidate pools. [Gao et al., 2023](https://proceedings.mlr.press/v202/gao23h.html) · [FLIP2](https://flip.protein.properties/)

The primary study covered imine reductase and three hydrophobic-core protein groups. Each group had ten matched starts with 100 initial measurements and a maximum of 100 additional measurements. Nine methods ran from each start. We focus here on three policies. Fixed reward retained its scoring rule, while the rule-based and Gemini-assisted policies could propose changes and stop after repeated failed checks. The primary starting samples ignored benchmark split labels. Searches revealed an existing score when they selected its variant, and the study evaluates those stored measurements. [Study design and results](../studies/multiprotein/four_protein_findings.md)

## Results

| Repair policy | Higher / tied / lower at actual stop | Higher / tied / lower at equal measurement count | Stopped after failed checks |
| --- | ---: | ---: | ---: |
| Rule-based | 0 / 35 / 5 | 0 / 39 / 1 | 35 / 40 |
| Gemini-assisted | 0 / 35 / 5 | 0 / 39 / 1 | 36 / 40 |

A tie uses an absolute score difference of at most 10⁻¹². Fixed reward used all 100 new measurements in every run. The retrospective equal-count analysis read the fixed-reward curve at the number of measurements used when each repair run stopped. The remaining loss for each policy occurred on imine reductase. [Saved evaluation](../../output/multiprotein/four_protein/matched_eval_51_60_report.json) · [Equal-count pairs](../../output/multiprotein/four_protein/matched_eval_51_60_same_measurements.json)

In the exploratory low-fitness-start Hydro comparison, each repair policy tied fixed reward in 5 of 30 starts and scored lower in 25 at actual stop. All 30 tied at equal measurement counts. The Hydro starting group was defined using measured fitness, so the stress test uses information that would generally be unavailable before measurement. Only six policy runs across the recorded studies had a full 30-measurement follow-up after a coverage warning. Those six covered three starts under both policies, with no reduction in the gap to the best measured score versus fixed reward. [Hydro stress test](../studies/multiprotein/hydro_low_fitness.md#findings) · [Follow-up results](submission_readiness.md#recovery-targets-in-the-synopsis)

## Interpretation and limitations

The primary actual-stop outcomes show how the implemented policies performed with a shared maximum budget. The equal-count comparison describes what fixed reward had found by the point where each repair policy stopped. Since the repair policy determines that comparison point, the results do not isolate the effect of changing the scoring rule. Ties in best scores allow different candidate histories. The repeated starts also share the same measured protein pools, and truncated follow-up limits the recovery analysis. The contribution is a traceable negative evaluation with both comparison points and explicit follow-up counts. Independent biological validation and causal estimates remain open. [Full project report](../../report/CERA_final_report.pdf)
