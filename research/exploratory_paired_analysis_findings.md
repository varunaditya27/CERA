# Exploratory paired analysis findings

This analysis was planned after the outcomes were seen, so it is **exploratory**, not a confirmatory test. Each comparison pairs ten starts on one fixed protein dataset. The outcome is the repair policy's best observed score at its actual stop minus fixed reward's best score at its actual stop. Repair often used fewer measurements, so this compares whole stopping policies, not repair alone at equal measurement counts. Scores have different scales across proteins.

| Protein | Mean difference, both repair policies | 95% resampling interval, both policies | Nonzero pairs | Unadjusted two-sided test | Adjusted test |
| --- | ---: | --- | ---: | ---: | ---: |
| IRED | -0.0280 | [-0.0841, 0] | 1 | 1 | 1 |
| Hydro P06241 | -0.0799 | [-0.1606, 0] | 3 | 0.25 | 1 |
| Hydro P01053 | 0 | [0, 0] | 0 | unavailable | unavailable |
| Hydro P0A9X9 | -0.0153 | [-0.0459, 0] | 1 | 1 | 1 |

Numbers are rounded for display. Both repair methods had the same final score differences in these runs. Intervals come from resampling the ten paired starts, and can be unstable with so many ties; the [0, 0] interval says the observed differences were all zero, not that the methods are equivalent. These starts reuse the same fixed data and do not represent independent biological replications. The signed-rank calculation assumes exchangeable signs under its null, which the study does not establish. The six available tests were adjusted as one family; the two all-zero tests are unavailable. No superiority, equivalence or cross-protein generalization claim is justified.

The [full record](../output/matched_eval_51_60_paired_analysis.json) contains each difference and both measurement counts, exact values, fingerprints and random seed. The [audit](../output/matched_eval_51_60_paired_analysis_audit.json) checked 80 pairs, reproduced the resampling and adjustment, and checked six test calculations against SciPy; for the single nonzero pair its two possible signs give a two-sided value of 1 directly. Run `OPENBLAS_NUM_THREADS=1 PYTHONPATH=backend python3 scripts/audit_paired_study_analysis.py output/matched_eval_51_60_report.json output/matched_eval_51_60_paired_analysis.json` to repeat it. The [protocol](exploratory_paired_analysis_protocol.md) explains the assumptions and source documentation.
