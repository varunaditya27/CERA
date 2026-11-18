# Submission readiness

Reviewed 18 November 2026. The original [synopsis](../Project_Synopsis.pdf) is the proposal and remains unchanged. The [project report for review](../output/pdf/CERA_final_report.pdf), its [editable source](CERA_final_report.tex), and the [project review presentation](../project_review.html) report what was actually built and measured. If a proposed claim conflicts with a measured result, use the result and its qualification from the report. Keep this repository with the report when following local evidence links.

## Core evidence

- The primary four-protein comparison comprises 360 terminal runs. Both repair policies achieved a higher best score than fixed reward in 0 of 40 matched starts, tied in 35 and scored lower in 5 at actual stop. Early stopping means measurement counts differ. [Results](multiprotein_study_findings.md).
- The separate IRED and Hydro shifted-start searches permit later selection from the eligible pool; they are not official held-out benchmark searches. Hydro initial membership uses fitness. [IRED](ired_low_change_findings.md); [Hydro](hydro_low_fitness_search_findings.md).
- Static held-out Hydro prediction ranges had low observed coverage; mixed and ridge predictors showed no consistent advantage across the reported measures. [Ridge study](heldout_shift_prediction_findings.md); [mixed study](mixed_heldout_findings.md).
- The system uses previously measured datasets. It does not establish causal repair benefit, biological validity of its warnings, or a general coverage guarantee. Repeated starts are not independent biological replications.

## Briefing guide crosswalk

Use this table with parts 5–7 of the [original briefing guide](../Project_Briefing_Guide.pdf) when preparing the report and oral evaluation.

| Planning question | What to report now |
| --- | --- |
| Which datasets were used? | Amylase was used for development. IRED and three separate Hydro protein groups were used for evaluation. GB1 and ProteinGym were catalogued as optional datasets. [Integrated results](project_status_and_results.md) · [Dataset sources](../data/SOURCES.md) |
| Which predictor and settings were used? | The main studies used five ridge models. Twenty of the 100 initial measurements set prediction ranges. The sequence representations average residue values and exclude boundary tokens and padding. The three-ridge, two-neural-network model was evaluated separately. [Representation checks](esm_feasibility_and_plan.md) · [Mixed predictor findings](mixed_heldout_findings.md) |
| What did Gemini and the repair checks contribute? | Gemini prioritized a finite menu of proposed changes. Local code checked each proposal. The repair cost used a normalized change in a weight plus 0.05 for changing a term. Later local-web and matched-study runs capture returned response text when the client makes it available. [Repair cost code](../backend/app/rewards/repair_menu.py) · [Completion evidence](completion_evidence_review.md) |
| How were warnings tested? | Controlled cases tested the software response to planted disagreements and checks for constraints and diversity. Accuracy against independently established biological failures remains unknown. [Disagreement findings](disagreement_warning_simulation_findings.md) · [Constraint and diversity findings](rule_warning_controls_findings.md) |
| How should the statistics be presented? | Report matched starts and actual numbers of measurements per policy. Paired intervals and signed-rank calculations were added after viewing the results. The same measured protein pool was reused across starts. [Primary results](multiprotein_study_findings.md) · [Paired analysis](exploratory_paired_analysis_findings.md) |
| Which course requirements still need confirmation? | The local documents leave guide approval, the institution’s final formatting requirements, and the briefing guide’s question about a reinforcement-learning requirement unresolved. The synopsis makes a paper conditional on the results. [Synopsis](../Project_Synopsis.pdf) |

The published [RVCE ISE curriculum](https://rvce.edu.in/sites/default/files/14.%20IS%202022%20Scheme%20III%20Year%20B.E.%20Programs_compressed_0.pdf) identifies data preparation, exploratory data analysis, prediction results, and a graphical demonstration in the IS353IA Part B section. It gives general course guidance. The batch-specific brief and required submission format still need confirmation.

| Course item | Evidence for the demonstration |
| --- | --- |
| Data preparation and exploratory data analysis | Walk through the measurements and splits using the [dataset presentation](../datasets.html), then open the [dataset evidence ledger](dataset_evidence_ledger.md) to show the source checks and unresolved details. |
| Model building and evaluation | Use the methods and results sections of the [report](../output/pdf/CERA_final_report.pdf). Explain why matched starts are useful and why early stopping changes the comparison. |
| Prediction results and graphical demonstration | Follow the local setup in the [README](../README.md). Open `/results` for the primary four-protein and Amylase comparisons. The walkthrough below covers `/experiments`, the saved review, and the decision check. Production HTTP checks verified both studies and matched the primary table against the saved evaluation. |

## Experiment demonstration

1. On `/experiments`, choose Amylase, the fixed default specification, five ridge models, and Fixed reward. Enter starting seed `13` and select **Run local experiment**. The starting seed reproduces the initial sample. This route requires the research dependencies and verified Amylase representation cache described in the [README](../README.md).
2. Open the completed entry under **Recent local runs**. Use the ten batches to show how a prediction is recorded before its measured score is revealed. This setup simulates 100 new measurements from the existing dataset and makes zero provider requests.
3. Select **Check recorded decisions**. The check replays the ten batch selections using the saved predictions. This fixed-reward run has zero repair proposals to replay.

The experiment submission API, completed-run listing, review, decision check, and three corresponding production pages passed a local HTTP walkthrough using a temporary run directory. Browser form interaction, visual layout, and assistive technology remain unchecked.

## Checks before submitting

1. Review the report and presentation with the project guide against the institution's required format, author names and assessment criteria. The repository does not establish those final administrative requirements; do not invent signatures or approvals.
2. The report PDF was rendered and checked for layout, and its source is included. Relative evidence links work in the repository layout; package supporting records if the report is moved elsewhere.
3. The local backend suite passed 188 tests, followed by three focused trace tests; the previously checked production frontend build and live local HTTP workflow are documented in the [status report](project_status_and_results.md). Browser visual, keyboard and screen-reader checks were not available. A new replay of the completed 360-run audit was stopped before completion; do not represent it as a passing check.
4. Decide, with the guide, whether a paper is appropriate. The synopsis makes a paper conditional; negative findings are reportable but do not establish a successful repair method.

## Research context

[ProteinGym](https://papers.nips.cc/paper_files/paper/2023/hash/cac723e5ff29f65e3fcbb0739ae91bee-Abstract-Datasets_and_Benchmarks.html) illustrates the need to report relevant prediction and design metrics. [FLIP2](https://flip.protein.properties/) defines different sequence and fitness splits. [WILDS](https://proceedings.mlr.press/v139/koh21a.html) demonstrates why results should be interpreted under the population shift actually tested. These sources provide context; they are not evidence that CERA's repair succeeds.
