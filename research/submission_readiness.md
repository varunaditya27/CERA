# Submission readiness

Reviewed 18 November 2026. The original [synopsis](../Project_Synopsis.pdf) is the proposal and remains unchanged. The [project report for review](../output/pdf/CERA_final_report.pdf), its [editable source](CERA_final_report.tex), and the [project review presentation](../project_review.html) report what was actually built and measured. If a proposed claim conflicts with a measured result, use the result and its qualification from the report. Keep this repository with the report when following local evidence links.

## Core evidence

- The primary four-protein comparison comprises 360 terminal runs. Both repair policies achieved a higher best score than fixed reward in 0 of 40 matched starts, tied in 35 and scored lower in 5 at actual stop. Early stopping means measurement counts differ. [Results](multiprotein_study_findings.md).
- The separate IRED and Hydro shifted-start searches permit later selection from the eligible pool; they are not official held-out benchmark searches. Hydro initial membership uses fitness. [IRED](ired_low_change_findings.md); [Hydro](hydro_low_fitness_search_findings.md).
- Static held-out Hydro prediction ranges had low observed coverage; mixed and ridge predictors showed no consistent advantage across the reported measures. [Ridge study](heldout_shift_prediction_findings.md); [mixed study](mixed_heldout_findings.md).
- The system uses previously measured datasets. It does not establish causal repair benefit, biological validity of its warnings, or a general coverage guarantee. Repeated starts are not independent biological replications.

## Checks before submitting

1. Review the report and presentation with the project guide against the institution's required format, author names and assessment criteria. The repository does not establish those final administrative requirements; do not invent signatures or approvals.
2. The report PDF was rendered and checked for layout, and its source is included. Relative evidence links work in the repository layout; package supporting records if the report is moved elsewhere.
3. The local backend suite passed 188 tests, followed by three focused trace tests; the previously checked production frontend build and live local HTTP workflow are documented in the [status report](project_status_and_results.md). Browser visual, keyboard and screen-reader checks were not available. A new replay of the completed 360-run audit was stopped before completion; do not represent it as a passing check.
4. Decide, with the guide, whether a paper is appropriate. The synopsis makes a paper conditional; negative findings are reportable but do not establish a successful repair method.

## Research context

[ProteinGym](https://papers.nips.cc/paper_files/paper/2023/hash/cac723e5ff29f65e3fcbb0739ae91bee-Abstract-Datasets_and_Benchmarks.html) illustrates the need to report relevant prediction and design metrics. [FLIP2](https://flip.protein.properties/) defines different sequence and fitness splits. [WILDS](https://proceedings.mlr.press/v139/koh21a.html) demonstrates why results should be interpreted under the population shift actually tested. These sources provide context; they are not evidence that CERA's repair succeeds.
