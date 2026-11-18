# Literature review

CERA studies a measurement decision. A model estimates a property for each candidate, a policy selects a batch, and previously recorded measurements reveal how that batch scored. The research question is whether warning-triggered changes to the policy improve search outcomes under the same maximum measurement budget.

## Benchmarks and changes in the test population

ProteinGym collects experimental measurements and evaluates fitness prediction and design across many assays. FLIP2 organizes evaluations by the type of change between training and test data, including the number of sequence changes and measured fitness. A method can perform differently across these settings, so the CERA report keeps the IRED and Hydro results separate and identifies how each starting pool was constructed. CERA’s sequential simulations permit later selection from the eligible measured pool. The static held-out checks answer a separate prediction question. [ProteinGym, 2023](https://papers.nips.cc/paper_files/paper/2023/hash/cac723e5ff29f65e3fcbb0739ae91bee-Abstract-Datasets_and_Benchmarks.html) · [FLIP2, 2026](https://flip.protein.properties/) · [CERA results](project_status_and_results.md)

## Learned scores and search behavior

Gao, Schulman and Hilton show in a synthetic preference-learning setup that optimization against a proxy score can depart from performance measured by their reference model. CERA uses that distinction when evaluating protein search. The selection rule uses predictions, while the evaluation uses previously measured scores. An accepted change passes local checks. Its value depends on what happens after the next measurements, including whether the policy stops early. The primary result reports both actual-stop and equal-count comparisons to show that difference. [Gao et al., 2023](https://proceedings.mlr.press/v202/gao23h.html) · [Primary study](multiprotein_study_findings.md)

## Prediction ranges and warning evaluation

Angelopoulos and Bates explain how conformal prediction turns calibration errors into prediction sets under assumptions about the relationship between calibration and test examples. A search selects candidates using its previous observations, and Hydro's fitness-defined split further changes the population being evaluated. CERA therefore reports observed coverage with its denominator. Synthetic cases measure how the implemented warning responds to known conditions. Later measurements give a different form of evidence, and a run that stops can leave too few observations to assess recovery. [Angelopoulos and Bates, 2021](https://arxiv.org/abs/2107.07511) · [Warning checks](submission_readiness.md#warning-checks-on-known-cases) · [Coverage after repair](after_repair_coverage_findings.md)

## Implications for the project

The literature motivates separating predictions, decisions, and outcomes. CERA’s results show that the tested repair policies frequently stopped early and did not improve final best scores in the primary comparison. Four of the five losses became ties at equal measurement counts. That comparison uses stopping points chosen by repair. A causal claim would require a study designed to separate the effect of changing the rule from the effect of stopping. [Report](../output/pdf/CERA_final_report.pdf)
