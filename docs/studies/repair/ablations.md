<div align="center">

# Repair ablations

Protocols and findings

</div>

## Stopping after failed repairs: protocol

Status: implementation and isolated development study, 17 November 2026. The earlier IRED study stopped after repeated failed repairs in all ten runs for both repair policies. That result motivates this exploratory analysis; do not treat the choice of comparison as independent of observed results. No IRED or Hydro data are used to select a setting here.

The question is what happens when the rule-based repair policy continues searching after repeated proposals fail verification. A failed proposal is still rejected, the previous reward is retained, and all hard constraints, warning checks, repair menus and verification remain active. The comparison changes only whether consecutive failed repairs stop the search. This is a test-only setting restricted to the Amylase development dataset, not a change to the default policy or permission to bypass constraints.

Run matched seeds 71–75 with identical 100 initial measurements, role and model seeds, candidate pool, fixed reward specification, targeted disagreement and direct diversity checks. Compare normal stopping with continuing after failed repairs. Both have at most 100 additional measurements. Use the existing rule-based repair selector; no provider calls. Save initial data, source and configuration fingerprints, all attempts, stop reasons, budgets and status, including failures. Evaluate after all planned runs have terminal status; preserve unequal actual measurement counts and do not pad stopped runs. Record when no proposal is accepted and when a run reaches the budget without ever meeting the stopping threshold. Report each seed and both policies, not only averages.

The comparison does not isolate the quality of the verification checks and cannot establish that a later result was caused by a particular repair. The normal policy and no-stop policy may receive different numbers of measurements and diverge after the original stopping point. Five starts on one development protein are not independent biological replications. The existing implementation retains the old reward when no change passes; a proposed separate 'no rollback' condition is not well defined independently of whether failed changes are applied. Do not rename this comparison as that missing ablation.

Check both policies on synthetic cases, reject disabling the stop outside Amylase development repair runs, and audit logged selections, repair replays, settings and measured scores independently. The [NeurIPS paper checklist](https://neurips.cc/public/guides/PaperChecklist) calls for sufficient experimental details to reproduce or verify results; record the scope and limitations of the audit rather than claiming every model was refit.

## Stopping after failed repairs: findings

The [protocol](ablations.md#stopping-after-failed-repairs-protocol) compares normal rule-based repair stopping with a development-only version that continues after repeated failed repairs. Both reject failed proposals, retain the prior reward and keep all hard constraints and verification checks. This Amylase comparison was motivated by already observed IRED results and is exploratory, not independent validation. No provider calls were made.

| Seed | Normal: new measurements / best score | Continue: new measurements / best score | Normal stop |
| ---: | ---: | ---: | --- |
| 71 | 100 / 0.194283 | 100 / 0.194283 | Budget exhausted |
| 72 | 100 / 0.186900 | 100 / 0.186900 | Budget exhausted |
| 73 | 40 / 0.178267 | 100 / 0.178267 | Failed repairs |
| 74 | 100 / 0.176983 | 100 / 0.176983 | Budget exhausted |
| 75 | 20 / 0.167933 | 100 / 0.169133 | Failed repairs |

The normal policy stopped early in two of five starts. The continuation policy used all 100 new measurements in every run. It found a higher best score in one pair and the same best score in four; in seed 75 the observed difference was 0.0012 on this dataset's score scale. This does not establish a causal effect of an individual repair, a reliable general advantage, or a result for other proteins. Continuing also used 140 additional measurements across the two early-stopped pairs. The two policies had the same starting observations within each seed.

Whole-run prediction ranges covered 307/360 newly measured scores for the normal policy and 426/500 for continuation. These include observations before and after accepted changes and should not be interpreted as after-repair coverage or an independent-sample confidence guarantee. The normal policy accepted two repairs across all runs, and continuation also accepted two. The [per-run summary](../../../output/amylase/repair/amylase_abstention_71_75/summary.csv) preserves individual denominators, widths, stops and action counts.

The [independent audit output](../../../output/amylase/repair/amylase_abstention_71_75_audit.json) is captured directly from the audit command: it checked ten runs, 86 selection batches and 73 repair replays. It reconstructed matched starts, selections, recorded source fingerprints, failure counts, stopping behavior, revealed scores and summary fields. It used saved predictions and distances and did not refit every predictor or prove scientific warning validity. The audit script SHA-256 was `a7f237baee94e52a7436d9fea105adf069cdd0fb26f0e87dcc0265889cee7589`; the manifest SHA-256 was `39d75627e8e7d9c89c87ed0e5f1574833233af59d39f747e5a8ca7828180704c`. The full backend suite passed 111 tests before the study. These five starts share one measured protein landscape.

## Removing repair terms: protocol

This exploratory Amylase study compares the existing rule-based policy against three versions that each disable one kind of reward-weight repair. The weights themselves remain in the reward; the ablation prevents triggered warnings from proposing a change to that term. The three adjustable terms are the distance penalty, uncertainty penalty and diversity bonus. Coverage and disagreement warnings both map to the uncertainty penalty, so disabling that term removes both repair routes together. This tests the implemented three-term library, not every possible numeric step within it.

Use matched seeds 91–95, 100 identical starting observations per seed, the same role and predictor seeds, all eligible unmeasured candidates, the pinned reward specification and at most 100 additional measurements. Compare four policies: all repairs available, and one policy with each term disabled. Keep warnings, hard constraints, evidence checks, stopping after failed repairs and the other repair routes active. A disabled route is logged as such and does not count as a failed proposal. No provider calls are needed.

The question is how each complete policy behaves when a repair route is unavailable. Policies can stop after different numbers of measurements and their later selections may diverge. Report actual budgets and per-seed outcomes without padding early stops. A route that never triggers is untested in that run. These five starts use one development protein and were planned after prior outcomes were inspected; they do not establish independent causal or biological generalization. Preserve configuration, source hashes, failed runs, attempted repairs, warnings and exact output records, and independently reconstruct selections, menu choices and disabled-route behavior before interpreting results. The [NeurIPS checklist](https://neurips.cc/public/guides/PaperChecklist) provides general guidance on reporting enough experimental detail for verification.

## Removing repair terms: findings

The [protocol](ablations.md#removing-repair-terms-protocol) compares the normal rule-based policy with three versions that each disable changing one reward term after warnings. The original reward terms, warning checks, evidence checks, hard constraints and stopping rule remain in place. This Amylase-only analysis was designed after earlier results were inspected and is exploratory, not independent biological validation. No provider calls were made.

| Policy | New measurements across five runs | Runs stopped after failed repairs | Disabled-route events | Best score compared with normal |
| --- | ---: | ---: | ---: | --- |
| Normal | 370 | 3/5 | 0 | Reference |
| No distance-penalty repair | 370 | 3/5 | 0 | Same in all 5 pairs |
| No uncertainty-penalty repair | 500 | 0/5 | 8 | Same in all 5 pairs |
| No diversity-bonus repair | 370 | 3/5 | 0 | Same in all 5 pairs |

The uncertainty term is shared by the coverage and disagreement repair routes, so both are disabled in that policy. It used 130 additional measurements across the five starts while ending with the same best score as normal in each pair. This does not prove the routes are unnecessary or that the policies are equivalent. No disabled-route event occurred in the distance or diversity removal runs, so those two removals did not exercise the corresponding intervention in this sample. No policy accepted a repair in these runs. Different policy paths and measurement counts limit causal interpretation, and five starts share one measured protein.

The [per-run summary](../../../output/amylase/repair/amylase_repair_terms_91_95/summary.csv) preserves coverage, range width, action counts and stop reasons. The [independent audit output](../../../output/amylase/repair/amylase_repair_terms_91_95_audit.json) was captured directly from the completed audit: it checked 20 runs, 161 selections and 63 repair replays, including warning/action order, disabled-route records, menu costs, source scores and matched starts. It used saved predictions and distances and did not refit every predictor or establish warning validity. The audit script SHA-256 was `39539bde881004a62d17b6d1164e315bce187f8f575c3fcfef5d804458a202c3`; it used `audit_development_repairs.py` SHA-256 `0774cd75ee9a53224b2b820b1c253f14b585b2bcab959fa3523145b4d43deaf5` and `audit_matched_proteins.py` SHA-256 `1200ae83da3d3d0ccfae5c4f6cf036876ba79eed4f9449e41ae36bc7af8c91e7`. The manifest SHA-256 was `c23f79e7bc9bd5ee9d221794acf10b6327cff4afbeab9d87b5d786b62d0cc968`. All 123 backend tests passed before the comparison.

## Retaining the prior reward: protocol

The current repair selector tries a fixed, cost-ordered menu. If no proposed change passes verification, it retains the prior reward and counts a failed repair. In this exploratory Amylase-only comparison, the alternative still runs and records every ordinary check and tries the same complete menu, but applies the final proposal when every proposal fails and that final proposal passes the menu and hard-constraint guard. It still counts the event as a failed repair, so the existing stop after repeated failures remains active. If the menu is empty or the final proposal fails the hard guard, the previous reward remains in place.

This is a precise ablation of immediate retention after unsuccessful proposals. It is not a test of reverting a previously accepted reward after later measured performance deteriorates; that later rollback mechanism is not implemented. The comparison differs from the evidence-gate ablation, which applies the first allowed proposal without waiting for the rest of the menu. Both experimental policies are restricted to the development dataset; neither changes hard sequence constraints, allowed parameter ranges or measurement budgets.

Compare five matched starts 111–115, normal versus alternative, with identical initial observations, model seeds, candidate access, pinned specification and at most 100 new measurements. Record every attempted check, any failed proposal applied, the consecutive-failure count, stop reason and actual measurements. Use rule-based repair and no provider calls. Validate synthetic examples where all proposals fail, an earlier proposal succeeds, the menu is empty and a hard guard rejects a proposal. Independently check the full menu and applied proposal, warning chronology, stopping, source scores and selections before reporting. Tests and the audit must show that regular study evaluation rejects the experimental mode.

This is a post-result-motivated development study on one measured protein. Policy paths can diverge after a failed proposal, and stopping can leave unequal measurements; do not interpret a difference as an independently established causal or biological benefit. The [NeurIPS checklist](https://neurips.cc/public/guides/PaperChecklist) calls for sufficient experimental details and reproducibility information to support interpretation.

## Retaining the prior reward: findings

The [protocol](ablations.md#retaining-the-prior-reward-protocol) compares the normal rule, which retains the previous reward when all proposals fail, with an Amylase-only alternative that applies the final permitted rejected proposal. Both still run the full checks, count the event as a failed repair, enforce menu and hard constraints, and stop after repeated failures. The comparison is exploratory and follows inspection of earlier results; it made no provider calls.

| Seed | New measurements per policy | Best score per policy | Selection batches that differed |
| ---: | ---: | ---: | ---: |
| 111 | 20 | 0.181200 | 0 / 2 |
| 112 | 40 | 0.166850 | 1 / 4 |
| 113 | 30 | 0.199933 | 0 / 3 |
| 114 | 40 | 0.186900 | 1 / 4 |
| 115 | 60 | 0.174683 | 1 / 6 |

All ten runs stopped after failed repairs. The alternative applied ten proposals that failed ordinary evidence checks, two per run. The final best scores and measurement counts matched within all five pairs, but three pairs selected different batches, so these outcomes do not establish policy equivalence. The normal policy's prediction ranges covered 132/190 newly measured scores and the alternative's covered 133/190; these are dependent whole-run observations, not evidence of a causal effect or independent-protein coverage guarantees. All five starts reuse one measured protein.

The [per-run summary](../../../output/amylase/repair/amylase_retention_111_115/summary.csv) retains range widths, action counts and stops. The [independent audit output](../../../output/amylase/repair/amylase_retention_111_115_audit.json), captured directly from the successful audit, reports ten runs, 38 selection batches and 55 repair replays. It checked matched starts, full attempted menus, rejected-proposal application, failure counts, stopping, selections and source scores. It used recorded predictions and distances and did not refit every predictor. A separate one-off calculation compared selected identifiers within pairs and was not saved as a reusable audit.

The audit script SHA-256 was `314b63c16a6bcae624ef484201cc3a749772567c0253a0eb5a6ff71d45aceb8b`; it used `audit_development_repairs.py` SHA-256 `55e6c1b2cfb0c89d599cf12ebfbb6d61676142755a759c269eb2e21fb49308eb` and `audit_matched_proteins.py` SHA-256 `b268174f1fbcd54104644b4bb24ced1387d1fc4546dfae09fbc2cb6b8de76ab4`. The study manifest SHA-256 was `cf04c05bce511844b507b8d91f20078ea64a7e231340d51153fcc3c07f8c1289`. The full backend suite passed 126 tests before the comparison, followed by 14 targeted tests after an additional experimental-setting guard.

This tests immediate retention after failed proposals. It does not implement or evaluate rolling back a previously accepted reward because later measured performance deteriorated.

## One repair penalty: protocol

The original proposal asks whether using one general penalty for every warning works differently from using a repair matched to the warning type. In this exploratory Amylase comparison, the general option always proposes increasing the existing uncertainty penalty. The normal option keeps the implemented mapping: distance for unfamiliar candidates, uncertainty for coverage or disagreement, and diversity for low batch diversity. A penalty is a subtraction from a candidate's predicted score; a larger uncertainty penalty makes uncertain candidates less attractive.

Both policies continue to run the original warning-specific checks. In particular, a proposal responding to a diversity warning must still satisfy the diversity check even though the common proposal changes uncertainty. Both retain the same cost-ordered steps, menu bounds, hard sequence and budget rules, verification, failed-repair stopping and rule-based selector. This changes the proposal term, not the definition of a warning or the evidence required to accept it. No provider calls are used.

Compare five matched starts 101–105 on the Amylase development dataset, with 100 identical initial measurements per pair, matched model seeds, the pinned reward specification, all eligible unmeasured candidates and at most 100 new measurements. Record the warning, actual proposed term, verification verdict, accepted changes, actual stop and measurement count. A warning type that never reaches repair is not tested by that run. Different choices can change later data and stopping, so outcomes compare complete policies; they do not isolate a causal effect of an individual weight change. Results are exploratory because earlier development and evaluation outcomes were inspected, and five starts reuse one protein.

Verify on synthetic data that normal mapping is unchanged, all warning types use the common term in the experimental policy, warning-specific evidence checks still apply, and ordinary study evaluators reject the experimental setting. Independently reconstruct selections, allowed menu, repair verdicts, action order and stopping before interpreting a real run. [Trabucco et al.](https://proceedings.mlr.press/v139/trabucco21a.html) discuss conservative objectives in model-based optimization, but their method is not the same as this project's simple penalty and does not validate this comparison.

## One repair penalty: findings

The [protocol](ablations.md#one-repair-penalty-protocol) compared the normal warning-specific repair mapping with an Amylase-only policy that proposes the uncertainty penalty for every warning while retaining the original warning-specific evidence checks. Five matched starts and both policies completed. This comparison was chosen after earlier outcomes had been inspected, uses one development protein and made no provider calls.

The comparison did **not exercise a difference in proposed repair term**. In each policy, the only repair actions that reached an attempt were four coverage actions and two disagreement actions; both warning types already map to the uncertainty penalty under the normal policy. No repair was accepted. All selected batches, stopping reasons, final best scores and measurement counts were identical within each pair. This is an inconclusive test of a universal penalty, not evidence that a universal penalty and type-specific repairs are equivalent.

| Seed | New measurements per policy | Best score per policy | Stop |
| ---: | ---: | ---: | --- |
| 101 | 100 | 0.170183 | Budget exhausted |
| 102 | 100 | 0.179767 | Budget exhausted |
| 103 | 40 | 0.199933 | Failed repairs |
| 104 | 100 | 0.176100 | Budget exhausted |
| 105 | 40 | 0.182250 | Failed repairs |

The [summary](../../../output/amylase/repair/amylase_universal_101_105/summary.csv) preserves per-run range coverage, widths and action counts. The [independent audit output](../../../output/amylase/repair/amylase_universal_101_105_audit.json) was captured directly from the completed audit: it checked ten runs, 76 selections and 36 repair replays, including matched starts, menu terms and costs, warning-specific checks, action order and stops. A separate one-off check compared selection identifiers in all five pairs; it was not saved as a reusable audit. The audit used saved predictions and distances rather than refitting every predictor.

The audit script SHA-256 was `efe33f03b560495f463c100c8b59c6b7825508c32371015fd0399dac8e4a871c`; it used `audit_development_repairs.py` SHA-256 `0774cd75ee9a53224b2b820b1c253f14b585b2bcab959fa3523145b4d43deaf5` and `audit_matched_proteins.py` SHA-256 `1a72b4a0ddcacd9194e3961c46d5746c05f5224001fca286f9ee234583c7315f`. The study manifest SHA-256 was `86f5c92070cf247c5d374bdbf7cb8b358633c7ac1093a8d873bbcaad0d2c2c70`. All 124 backend tests passed before the runs.

## Repair evidence gate: protocol

This exploratory Amylase-only comparison studies the effect of the evidence gate that decides whether a candidate repair is accepted. Five matched seeds 81–85 compare the existing rule-based repair policy with a version that applies the first eligible cost-ordered proposal without requiring its evidence checks to pass. Both policies keep the same starts, candidate pool, budget, warning rules, repair menu and stop after repeated failed repairs. They make no provider calls. The choice of this comparison follows inspection of prior results and is not an independent confirmatory study.

For auditability, the comparison still **calculates and records** the normal verifier's checks for every proposed change, but the ablated policy ignores the scientific-evidence verdict when deciding whether to apply an otherwise permitted proposal. The allowlisted repair menu, validated reward specification, batch selection, sequence constraints and measurement-budget enforcement remain active. Thus this is an ablation of the evidence gate, not removal of input validation or a test of unsafe sequences. It does not test later rollback after a previously accepted change.

Use the same Amylase initial and role sampling rules and at most 100 new measurements per run. Record which applied changes the ordinary verifier would have rejected, all attempts and stops, scores and range coverage. Never use unmeasured scores when selecting or modifying a reward. Report each pair and actual measurement counts, retain failed or incomplete runs, and do not assume results generalize beyond this one development landscape. Comparisons are between complete policies: different accepted changes and early stops can lead to different subsequent observations.

Before interpreting results, test the normal and ablated decisions on invented data, reject ablation outside Amylase development repair mode, and independently reconstruct saved selections, repair checks and applicable acceptance rules. A reviewer must be able to distinguish a simulated gate bypass from a verified proposal. As the [NeurIPS checklist](https://neurips.cc/public/guides/PaperChecklist) recommends, preserve the experimental configuration, measurements and limits needed to reproduce or verify the result.

## Repair evidence gate: findings

The [protocol](ablations.md#repair-evidence-gate-protocol) compares the normal rule-based repair policy with an Amylase-only version that applies the first permitted repair proposal even when its scientific-evidence checks fail. The checks are still computed and logged; menu validity, hard sequence constraints and the measurement budget remain enforced. This post-result-motivated development comparison is not an independent test of all verifier components or evidence about another protein.

| Seed | Normal: new measurements / best score | Evidence gate bypassed: new measurements / best score | Normal stop | Bypass stop |
| ---: | ---: | ---: | --- | --- |
| 81 | 70 / 0.171083 | 100 / 0.171083 | Failed repairs | Budget exhausted |
| 82 | 30 / 0.176050 | 90 / 0.176050 | Failed repairs | Failed repairs |
| 83 | 40 / 0.176050 | 100 / 0.194283 | Failed repairs | Budget exhausted |
| 84 | 30 / 0.211633 | 100 / 0.211633 | Failed repairs | Budget exhausted |
| 85 | 30 / 0.176983 | 100 / 0.176983 | Failed repairs | Budget exhausted |

The normal policy stopped after failed repairs in all five runs and used 200 new measurements in total. The bypass policy used 490, stopped after failed repairs once and found a higher best score in one pair; the other four final best scores matched. It accepted 30 changes, 29 of which the ordinary evidence checks would have rejected; the normal policy accepted none. Different repairs and 290 additional measurements both affect the policies' later paths, so the one higher result cannot be attributed solely to the evidence gate. Five matched starts on one protein do not establish a general advantage.

Whole-run prediction ranges covered 141/200 newly measured scores for normal repair and 379/490 for the bypass. These include observations before and after accepted repairs and are not an after-repair coverage estimate or an independent-sample guarantee. Full per-run values and action counts are in the [summary](../../../output/amylase/repair/amylase_verifier_81_85/summary.csv).

The [independent audit output](../../../output/amylase/repair/amylase_verifier_81_85_audit.json) is captured directly from the completed audit: it checked ten runs, 69 selections and 60 repair replays. It checked matching starts, source fingerprints, selection reconstruction, repair-menu order and costs, stopping behavior, source scores and the number of accepted proposals that failed the ordinary evidence checks. It did not refit every predictor or independently establish scientific validity of each check. The audit script SHA-256 was `d166330ec403ec2e2e2a477a760f5c17195a08c515ef57fa9db1b73aedc0e28e`; it also used `audit_development_repairs.py` SHA-256 `0774cd75ee9a53224b2b820b1c253f14b585b2bcab959fa3523145b4d43deaf5` and `audit_matched_proteins.py` SHA-256 `dd22c8251eb87cd44021ca6ed339bb4775c4a09e845b8f91d1445e3397fb4655`. The study manifest SHA-256 was `a5392a0c6e0c2e44ca4e344abf6f3494506ce15e2d2c5ff4c652e6c5e2cbb453`. All 121 backend tests passed before the comparison, and no provider calls were made.

Provenance correction: these run records label the reward origin `abstention_development` because the shared runner used a fixed label, even though the manifest correctly identifies the `evidence` comparison. This metadata error did not choose the reward or alter the experiment; the original records are preserved. Later runs use the comparison-specific origin label.
