<div align="center">

# Exploratory paired analysis of the four-protein study

Protocol and findings

</div>

## Protocol

This plan was written **after the study findings were inspected**. It is exploratory and cannot retroactively make the comparisons prespecified. The question is the difference in best observed score at each policy's actual stop, for each of four fixed protein datasets, comparing each of the two repair policies with fixed reward. The ten matching starting seeds are the resampling units; they are repeated starts on the same measured dataset, not ten independent proteins or laboratory experiments. Keep scores on each protein's own scale. Different stopping counts are part of the policy comparison and must be displayed.

For each of eight comparisons, report all ten differences and measurement counts, their mean, and a two-sided 95% percentile interval from 20,000 resamples of the ten paired differences with replacement, using a fixed random seed. The interval describes sensitivity to these starts under the resampling assumptions; with ten heavily tied observations it can be unstable or degenerate and must not be read as a guarantee or population-wide biological uncertainty. The percentile approach is simple but [SciPy cautions that it is rarely used in practice](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html); it is used here for an explicitly descriptive interval and avoids treating a degenerate bootstrap as a successful bias-corrected interval.

Also report a two-sided paired signed-rank test, excluding exactly zero differences, using all sign permutations for the nonzero differences; the null assumes their signs are exchangeable, a condition not established by these observational runs. Ties in absolute differences get average ranks. All-zero comparisons are reported as unavailable rather than as evidence of equality. Adjust the eight available p-values as a family with Holm's step-down method, and show unadjusted values. No significance or equivalence claim follows from this post-result analysis. The [SciPy signed-rank documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.wilcoxon.html) notes the need to handle ties, zeros and numerical differences explicitly. Use the existing 1e-12 score tie rule for signed-rank inputs; retain unrounded differences for means and intervals.

Reject missing, duplicate or incomplete seed/method records. Save the input report fingerprint, code fingerprint, library version, seeds, all observations and results. Test all-zero and tied examples and independently check the finite sign permutation on small fixtures. The input report itself is an audited retrospective artifact, not independent verification of its predictor fits.

## Findings

This analysis was planned after the outcomes were seen, so it is **exploratory**, not a confirmatory test. Each comparison pairs ten starts on one fixed protein dataset. The outcome is the repair policy's best observed score at its actual stop minus fixed reward's best score at its actual stop. Repair often used fewer measurements, so this compares whole stopping policies, not repair alone at equal measurement counts. Scores have different scales across proteins.

| Protein | Mean difference, both repair policies | 95% resampling interval, both policies | Nonzero pairs | Unadjusted two-sided test | Adjusted test |
| --- | ---: | --- | ---: | ---: | ---: |
| IRED | -0.0280 | [-0.0841, 0] | 1 | 1 | 1 |
| Hydro P06241 | -0.0799 | [-0.1606, 0] | 3 | 0.25 | 1 |
| Hydro P01053 | 0 | [0, 0] | 0 | unavailable | unavailable |
| Hydro P0A9X9 | -0.0153 | [-0.0459, 0] | 1 | 1 | 1 |

Numbers are rounded for display. Both repair methods had the same final score differences in these runs. Intervals come from resampling the ten paired starts, and can be unstable with so many ties; the [0, 0] interval says the observed differences were all zero, not that the methods are equivalent. These starts reuse the same fixed data and do not represent independent biological replications. The signed-rank calculation assumes exchangeable signs under its null, which the study does not establish. The six available tests were adjusted as one family; the two all-zero tests are unavailable. No superiority, equivalence or cross-protein generalization claim is justified.

The [full record](../../../output/matched_eval_51_60_paired_analysis.json) contains each difference and both measurement counts, exact values, fingerprints and random seed. The [audit](../../../output/matched_eval_51_60_paired_analysis_audit.json) checked 80 pairs, reproduced the resampling and adjustment, and checked six test calculations against SciPy; for the single nonzero pair its two possible signs give a two-sided value of 1 directly. Run `OPENBLAS_NUM_THREADS=1 PYTHONPATH=backend:. python3 -m scripts.reporting.audit_paired_study_analysis output/matched_eval_51_60_report.json output/matched_eval_51_60_paired_analysis.json` to repeat it. The [protocol](paired_analysis.md#protocol) explains the assumptions and source documentation.
