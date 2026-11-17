# Development comparison: retaining the prior reward

The [protocol](retention_ablation_protocol.md) compares the normal rule, which retains the previous reward when all proposals fail, with an Amylase-only alternative that applies the final permitted rejected proposal. Both still run the full checks, count the event as a failed repair, enforce menu and hard constraints, and stop after repeated failures. The comparison is exploratory and follows inspection of earlier results; it made no provider calls.

| Seed | New measurements per policy | Best score per policy | Selection batches that differed |
| ---: | ---: | ---: | ---: |
| 111 | 20 | 0.181200 | 0 / 2 |
| 112 | 40 | 0.166850 | 1 / 4 |
| 113 | 30 | 0.199933 | 0 / 3 |
| 114 | 40 | 0.186900 | 1 / 4 |
| 115 | 60 | 0.174683 | 1 / 6 |

All ten runs stopped after failed repairs. The alternative applied ten proposals that failed ordinary evidence checks, two per run. The final best scores and measurement counts matched within all five pairs, but three pairs selected different batches, so these outcomes do not establish policy equivalence. The normal policy's prediction ranges covered 132/190 newly measured scores and the alternative's covered 133/190; these are dependent whole-run observations, not evidence of a causal effect or independent-protein coverage guarantees. All five starts reuse one measured protein.

The [per-run summary](../output/amylase_retention_111_115/summary.csv) retains range widths, action counts and stops. The [independent audit output](../output/amylase_retention_111_115_audit.json), captured directly from the successful audit, reports ten runs, 38 selection batches and 55 repair replays. It checked matched starts, full attempted menus, rejected-proposal application, failure counts, stopping, selections and source scores. It used recorded predictions and distances and did not refit every predictor. A separate one-off calculation compared selected identifiers within pairs and was not saved as a reusable audit.

The audit script SHA-256 was `314b63c16a6bcae624ef484201cc3a749772567c0253a0eb5a6ff71d45aceb8b`; it used `audit_development_repairs.py` SHA-256 `55e6c1b2cfb0c89d599cf12ebfbb6d61676142755a759c269eb2e21fb49308eb` and `audit_matched_proteins.py` SHA-256 `b268174f1fbcd54104644b4bb24ced1387d1fc4546dfae09fbc2cb6b8de76ab4`. The study manifest SHA-256 was `cf04c05bce511844b507b8d91f20078ea64a7e231340d51153fcc3c07f8c1289`. The full backend suite passed 126 tests before the comparison, followed by 14 targeted tests after an additional experimental-setting guard.

This tests immediate retention after failed proposals. It does not implement or evaluate rolling back a previously accepted reward because later measured performance deteriorated.
