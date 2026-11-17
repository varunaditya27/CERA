# Controlled model-ranking disagreement findings

The [protocol](disagreement_warning_simulation_protocol.md) constructed 45 matched sets of ten synthetic candidates under each of three conditions: five identical model rankings, one model with a single rank-pair swap, and one model with a fully reversed ranking. The cases are permutations of a small family of constructed patterns, not independent proteins or experimental fitness measurements.

| Planted condition | Warnings | No warning | Average pairwise correlation range |
| --- | ---: | ---: | ---: |
| All identical | 0/45 | 45/45 | 1.000 |
| One model swaps two ranks | 0/45 | 45/45 | 0.607–0.995 |
| One model fully reversed | 45/45 | 0/45 | 0.200 |

The warning's existing threshold is an average pairwise correlation below 0.5. All single-swap cases were above that threshold; every constructed reversal was below it. If any planted ranking change is labeled positive, the swapped-versus-identical comparison has recall 0/45, zero false alarms among the 45 identical cases, undefined precision because no cases triggered, and F1 0. The reversed-versus-identical comparison has recall 45/45, precision 45/45, zero false alarms among 45 negatives and F1 1. These numbers describe deliberately chosen cases and an artificial equal mixture; they are not prevalence-adjusted or real-world accuracy estimates.

The [simulation output](../output/disagreement_warning_simulation.json) preserves all 135 planted member-prediction matrices, warning groups, values, statuses and code fingerprints. The separately captured [audit output](../output/disagreement_warning_simulation_audit.json) confirms that an independent rank calculation reconstructed all cases without calling the warning. Tests also check tied-rank arithmetic and rejection of altered member predictions. The simulation output SHA-256 was `87a8305747eebf0ccc862228c8f2381a7364df951f50f9e4c8eb1aa896586fa9`; the audit script SHA-256 was `2b561ae26f191ebf7653aa959bbe14a42b40ddbbfb278241951bb1e4890ec9a3`. All 133 backend tests passed before the run.

Disagreement among model members does not establish which model is right, whether the group prediction is wrong, or whether a repair improves a later search. The separate [Amylase ranking analysis](disagreement_ranking_findings.md) compares selected-batch predictions with subsequently measured scores but also does not establish warning accuracy on other proteins. No protein scores, model settings, warning thresholds or provider settings were changed in this simulation.
