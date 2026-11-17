# Development comparison: removing repair terms

The [protocol](repair_terms_ablation_protocol.md) compares the normal rule-based policy with three versions that each disable changing one reward term after warnings. The original reward terms, warning checks, evidence checks, hard constraints and stopping rule remain in place. This Amylase-only analysis was designed after earlier results were inspected and is exploratory, not independent biological validation. No provider calls were made.

| Policy | New measurements across five runs | Runs stopped after failed repairs | Disabled-route events | Best score compared with normal |
| --- | ---: | ---: | ---: | --- |
| Normal | 370 | 3/5 | 0 | Reference |
| No distance-penalty repair | 370 | 3/5 | 0 | Same in all 5 pairs |
| No uncertainty-penalty repair | 500 | 0/5 | 8 | Same in all 5 pairs |
| No diversity-bonus repair | 370 | 3/5 | 0 | Same in all 5 pairs |

The uncertainty term is shared by the coverage and disagreement repair routes, so both are disabled in that policy. It used 130 additional measurements across the five starts while ending with the same best score as normal in each pair. This does not prove the routes are unnecessary or that the policies are equivalent. No disabled-route event occurred in the distance or diversity removal runs, so those two removals did not exercise the corresponding intervention in this sample. No policy accepted a repair in these runs. Different policy paths and measurement counts limit causal interpretation, and five starts share one measured protein.

The [per-run summary](../output/amylase_repair_terms_91_95/summary.csv) preserves coverage, range width, action counts and stop reasons. The [independent audit output](../output/amylase_repair_terms_91_95_audit.json) was captured directly from the completed audit: it checked 20 runs, 161 selections and 63 repair replays, including warning/action order, disabled-route records, menu costs, source scores and matched starts. It used saved predictions and distances and did not refit every predictor or establish warning validity. The audit script SHA-256 was `39539bde881004a62d17b6d1164e315bce187f8f575c3fcfef5d804458a202c3`; it used `audit_development_repairs.py` SHA-256 `0774cd75ee9a53224b2b820b1c253f14b585b2bcab959fa3523145b4d43deaf5` and `audit_matched_proteins.py` SHA-256 `1200ae83da3d3d0ccfae5c4f6cf036876ba79eed4f9449e41ae36bc7af8c91e7`. The manifest SHA-256 was `c23f79e7bc9bd5ee9d221794acf10b6327cff4afbeab9d87b5d786b62d0cc968`. All 123 backend tests passed before the comparison.
