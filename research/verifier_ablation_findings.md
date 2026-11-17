# Development comparison: repair evidence gate

The [protocol](verifier_ablation_protocol.md) compares the normal rule-based repair policy with an Amylase-only version that applies the first permitted repair proposal even when its scientific-evidence checks fail. The checks are still computed and logged; menu validity, hard sequence constraints and the measurement budget remain enforced. This post-result-motivated development comparison is not an independent test of all verifier components or evidence about another protein.

| Seed | Normal: new measurements / best score | Evidence gate bypassed: new measurements / best score | Normal stop | Bypass stop |
| ---: | ---: | ---: | --- | --- |
| 81 | 70 / 0.171083 | 100 / 0.171083 | Failed repairs | Budget exhausted |
| 82 | 30 / 0.176050 | 90 / 0.176050 | Failed repairs | Failed repairs |
| 83 | 40 / 0.176050 | 100 / 0.194283 | Failed repairs | Budget exhausted |
| 84 | 30 / 0.211633 | 100 / 0.211633 | Failed repairs | Budget exhausted |
| 85 | 30 / 0.176983 | 100 / 0.176983 | Failed repairs | Budget exhausted |

The normal policy stopped after failed repairs in all five runs and used 200 new measurements in total. The bypass policy used 490, stopped after failed repairs once and found a higher best score in one pair; the other four final best scores matched. It accepted 30 changes, 29 of which the ordinary evidence checks would have rejected; the normal policy accepted none. Different repairs and 290 additional measurements both affect the policies' later paths, so the one higher result cannot be attributed solely to the evidence gate. Five matched starts on one protein do not establish a general advantage.

Whole-run prediction ranges covered 141/200 newly measured scores for normal repair and 379/490 for the bypass. These include observations before and after accepted repairs and are not an after-repair coverage estimate or an independent-sample guarantee. Full per-run values and action counts are in the [summary](../output/amylase_verifier_81_85/summary.csv).

The [independent audit output](../output/amylase_verifier_81_85_audit.json) is captured directly from the completed audit: it checked ten runs, 69 selections and 60 repair replays. It checked matching starts, source fingerprints, selection reconstruction, repair-menu order and costs, stopping behavior, source scores and the number of accepted proposals that failed the ordinary evidence checks. It did not refit every predictor or independently establish scientific validity of each check. The audit script SHA-256 was `d166330ec403ec2e2e2a477a760f5c17195a08c515ef57fa9db1b73aedc0e28e`; it also used `audit_development_repairs.py` SHA-256 `0774cd75ee9a53224b2b820b1c253f14b585b2bcab959fa3523145b4d43deaf5` and `audit_matched_proteins.py` SHA-256 `dd22c8251eb87cd44021ca6ed339bb4775c4a09e845b8f91d1445e3397fb4655`. The study manifest SHA-256 was `a5392a0c6e0c2e44ca4e344abf6f3494506ce15e2d2c5ff4c652e6c5e2cbb453`. All 121 backend tests passed before the comparison, and no provider calls were made.

Provenance correction: these run records label the reward origin `abstention_development` because the shared runner used a fixed label, even though the manifest correctly identifies the `evidence` comparison. This metadata error did not choose the reward or alter the experiment; the original records are preserved. Later runs use the comparison-specific origin label.
