# Submission readiness

Reviewed 18 November 2026. The original [synopsis](../Project_Synopsis.pdf) is the proposal and remains unchanged. The [project report for review](../output/pdf/CERA_final_report.pdf), its [editable source](CERA_final_report.tex), and the [project review presentation](../project_review.html) report what was actually built and measured. If a proposed claim conflicts with a measured result, use the result and its qualification from the report. Keep this repository with the report when following local evidence links.

For a review copy, extract the submission ZIP as one folder and open this file, the report, or the presentation from inside it. The archive includes the materials directly cited by these three files and selected machine-readable evaluation summaries. Use the full repository for the application, raw data, and complete replay records.

The [standalone literature review](literature_review.md) connects the benchmark, reward, and prediction-range research to the implemented evaluation. It accompanies the report and the original proposal.

## Core evidence

- The primary four-protein comparison comprises 360 terminal runs. Both repair policies achieved a higher best score than fixed reward in 0 of 40 matched starts, tied in 35 and scored lower in 5 at actual stop. Early stopping means measurement counts differ. [Results](multiprotein_study_findings.md).
- A later comparison at the same measurement count found 39 ties and one lower score per repair policy. It uses each repair run's stopping point as the comparison count. [Paired scores](../output/matched_eval_51_60_same_measurements.json)
- The separate IRED and Hydro shifted-start searches permit later selection from the eligible pool; they are not official held-out benchmark searches. Hydro initial membership uses fitness. [IRED](ired_low_change_findings.md); [Hydro](hydro_low_fitness_search_findings.md).
- Static held-out Hydro prediction ranges had low observed coverage; mixed and ridge predictors showed no consistent advantage across the reported measures. [Ridge study](heldout_shift_prediction_findings.md); [mixed study](mixed_heldout_findings.md).
- The system uses previously measured datasets. It does not establish causal repair benefit, biological validity of its warnings, or a general coverage guarantee. Repeated starts are not independent biological replications.

## Warning checks on known cases

The synopsis asks for precision and recall for each warning. Precision is the share of warnings that matched a labeled positive case. Recall is the share of labeled positive cases that triggered a warning. The fractions below show how many cases each percentage represents. [Precision definition](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.precision_score.html) · [Recall definition](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.recall_score.html)

| Warning | Positive case | Precision | Recall |
| --- | --- | ---: | ---: |
| Coverage | Moderate undercoverage | 239/245 (97.6%) | 239/1,000 (23.9%) |
| Coverage | Severe undercoverage | 946/952 (99.4%) | 946/1,000 (94.6%) |
| Unfamiliar candidates | Distant candidates with a 10% miss probability | 74/74 (100%) | 74/1,000 (7.4%) |
| Unfamiliar candidates | Distant candidates with a 50% miss probability | 943/943 (100%) | 943/1,000 (94.3%) |
| Model disagreement | One model swaps two ranks | Undefined (zero warnings) | 0/45 (0%) |
| Model disagreement | One model reverses its ranking | 45/45 (100%) | 45/45 (100%) |
| Constraint | Hand-picked rule violation | 7/7 (100%) | 7/7 (100%) |
| Diversity | Hand-picked batch below the rule threshold | 2/2 (100%) | 2/2 (100%) |

The coverage, unfamiliar-candidate, and disagreement comparisons use equal numbers of constructed positive and reference cases. The unfamiliar-candidate reference cannot trigger by construction. The constraint and diversity cases test implementation, and one diversity case was excluded because its batch contained only one variant. These checks establish behavior on the stated cases. Accuracy on new laboratory outcomes remains unknown. [Coverage counts](../output/coverage_warning_simulation.json) · [Unfamiliar-candidate counts](../output/support_warning_simulation.json) · [Disagreement counts](../output/disagreement_warning_simulation.json) · [Rule-control counts](../output/rule_warning_controls.json)

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

The experiment submission API, completed-run listing, review, decision check, and three corresponding production pages passed a local HTTP walkthrough using a temporary run directory. Playwright Chromium also verified keyboard submission, opening batch details, scrolling its table with the keyboard, and reaching the passing decision check at 390 px wide. The audit checked ten batch selections for the fixed-reward run. Screen-reader behavior remains unchecked.

## Checks before submitting

1. Review the report and presentation with the project guide against the institution's required format, author names and assessment criteria. The repository does not establish those final administrative requirements; do not invent signatures or approvals.
2. The report PDF was rendered and checked for layout, and its source is included. Relative evidence links work in the repository layout; package supporting records if the report is moved elsewhere.
3. The latest full backend run passed 189 tests. The production frontend build and live HTTP workflow also passed their checks. Playwright verified the demo flow and keyboard navigation through all 14 presentation slides at 390 px wide. Desktop Results and mobile review screenshots were inspected. Screen-reader behavior remains unchecked. The earlier 360-run study has a recorded audit, and the later replay was stopped before completion. [Status report](project_status_and_results.md)
4. Decide, with the guide, whether a paper is appropriate. The synopsis makes a paper conditional; negative findings are reportable but do not establish a successful repair method.

## Research context

[ProteinGym](https://papers.nips.cc/paper_files/paper/2023/hash/cac723e5ff29f65e3fcbb0739ae91bee-Abstract-Datasets_and_Benchmarks.html) illustrates the need to report relevant prediction and design metrics. [FLIP2](https://flip.protein.properties/) defines different sequence and fitness splits. [WILDS](https://proceedings.mlr.press/v139/koh21a.html) demonstrates why results should be interpreted under the population shift actually tested. These sources provide context; they are not evidence that CERA's repair succeeds.
