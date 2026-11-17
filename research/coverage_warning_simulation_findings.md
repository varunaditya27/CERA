# Controlled coverage-warning simulation findings

The [protocol](coverage_warning_simulation_protocol.md) generated 1,000 independent 30-observation windows at each of three known coverage probabilities, then applied the existing warning rule. The probabilities are illustrative synthetic conditions, not estimates from protein datasets. The warning fires when at most 22 of 30 observations are covered.

| Assumed coverage probability | Meaning in this simulation | Warnings | No warning | Exact warning probability under the independent model |
| ---: | --- | ---: | ---: | ---: |
| 90% | Nominal reference | 6/1,000 | 994/1,000 | 0.78% |
| 80% | Moderate undercoverage | 239/1,000 | 761/1,000 | 23.92% |
| 60% | Severe undercoverage | 946/1,000 | 54/1,000 | 95.65% |

Under this particular independent model, the rule is much more likely to flag severe undercoverage than a moderate drop from the 90% target. That is consistent with its lower trigger threshold and a 30-observation window; it is not evidence that real adaptive protein searches have these rates. The 90% case's 6/1,000 warning rate is a false-alarm rate only for this synthetic reference condition.

For an artificial mixture of 1,000 moderate-undercoverage windows and 1,000 nominal windows, the observed precision was 239/245 (97.6%), recall 239/1,000 (23.9%) and F1 about 0.384. For the corresponding severe-versus-nominal mixture, precision was 946/952 (99.4%), recall 946/1,000 (94.6%) and F1 about 0.969. These precision and F1 values depend on the chosen equal mixture and must not be treated as estimates for an unknown real-world prevalence. All 3,000 warnings had an available status.

The [simulation output](../output/coverage_warning_simulation.json) records the seed, conditions, counts, exact binomial probabilities, source fingerprints and software versions. The [audit output](../output/coverage_warning_simulation_audit.json) was captured directly from a separate reproducible audit. It regenerated all 3,000 windows without calling the warning function, independently checked the threshold and counts, and checked exact probabilities against SciPy's binomial calculation. It also rejects changed fingerprints or counts. The simulation output SHA-256 was `10383cf71f3dbd6e0a01b3966522e54466b173228c3389b9de2c500daa456aab`; the audit script SHA-256 was `b7c5afd952317e6d3955608781ccd68c6ab5d4c9cda6bd739931b913e5704380`. All 129 backend tests passed before the run.

The independent, fixed-probability assumption is deliberately simpler than the adaptive selection in CERA. This analysis does not validate the coverage warning on real protein searches, establish a biological failure rate, or evaluate the other warning types. No model, dataset, warning threshold or provider setting was changed.
