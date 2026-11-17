# Development comparison: stopping after failed repairs

The [protocol](abstention_ablation_protocol.md) compares normal rule-based repair stopping with a development-only version that continues after repeated failed repairs. Both reject failed proposals, retain the prior reward and keep all hard constraints and verification checks. This Amylase comparison was motivated by already observed IRED results and is exploratory, not independent validation. No provider calls were made.

| Seed | Normal: new measurements / best score | Continue: new measurements / best score | Normal stop |
| ---: | ---: | ---: | --- |
| 71 | 100 / 0.194283 | 100 / 0.194283 | Budget exhausted |
| 72 | 100 / 0.186900 | 100 / 0.186900 | Budget exhausted |
| 73 | 40 / 0.178267 | 100 / 0.178267 | Failed repairs |
| 74 | 100 / 0.176983 | 100 / 0.176983 | Budget exhausted |
| 75 | 20 / 0.167933 | 100 / 0.169133 | Failed repairs |

The normal policy stopped early in two of five starts. The continuation policy used all 100 new measurements in every run. It found a higher best score in one pair and the same best score in four; in seed 75 the observed difference was 0.0012 on this dataset's score scale. This does not establish a causal effect of an individual repair, a reliable general advantage, or a result for other proteins. Continuing also used 140 additional measurements across the two early-stopped pairs. The two policies had the same starting observations within each seed.

Whole-run prediction ranges covered 307/360 newly measured scores for the normal policy and 426/500 for continuation. These include observations before and after accepted changes and should not be interpreted as after-repair coverage or an independent-sample confidence guarantee. The normal policy accepted two repairs across all runs, and continuation also accepted two. The [per-run summary](../output/amylase_abstention_71_75/summary.csv) preserves individual denominators, widths, stops and action counts.

The [independent audit output](../output/amylase_abstention_71_75_audit.json) is captured directly from the audit command: it checked ten runs, 86 selection batches and 73 repair replays. It reconstructed matched starts, selections, recorded source fingerprints, failure counts, stopping behavior, revealed scores and summary fields. It used saved predictions and distances and did not refit every predictor or prove scientific warning validity. The audit script SHA-256 was `a7f237baee94e52a7436d9fea105adf069cdd0fb26f0e87dcc0265889cee7589`; the manifest SHA-256 was `39d75627e8e7d9c89c87ed0e5f1574833233af59d39f747e5a8ca7828180704c`. The full backend suite passed 111 tests before the study. These five starts share one measured protein landscape.
