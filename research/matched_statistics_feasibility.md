# Feasibility of further statistical reporting

Reviewed 2026-11-17 using the already evaluated [four-protein report](../output/matched_eval_51_60_report.json). This is a post-result feasibility review, not a prespecified significance analysis. The original synopsis asks for 95% bootstrap intervals and paired Wilcoxon signed-rank tests; these have not yet been performed as the planned formal analysis.

For each protein, the existing report contains ten paired starting seeds per method, final best scores, actual measurement counts and recovery summaries. A fresh read-only count of exact final-score differences between each repair method and fixed reward gives:

| Protein | Equal pairs | Repair higher | Repair lower | Applies to |
| --- | ---: | ---: | ---: | --- |
| IRED | 9 | 0 | 1 | Each repair method |
| Hydro P06241 | 7 | 0 | 3 | Each repair method |
| Hydro P01053 | 10 | 0 | 0 | Each repair method |
| Hydro P0A9X9 | 9 | 0 | 1 | Each repair method |

These exact-zero counts agree here with the published findings, which used an absolute tie tolerance of 1e-12. The comparison is at each policy's actual stop, so the repair policies often have fewer measurements than fixed reward. It assesses the implemented policies under a shared maximum budget; it does not isolate the effect of a repair at the same measurement count or establish equivalence.

The installed SciPy version is 1.18.1. Its [signed-rank documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.wilcoxon.html) warns that ties and zero differences change the null distribution and that an all-zero sample can make some calculation methods undefined. A hypothesis test needs a stated null, alternative, zero handling, tie handling and comparison family; choosing these after seeing these values makes the analysis exploratory. Ten seeds are repeated starts on each same dataset, not ten independently sampled proteins. The four score scales differ, so raw score differences should not be pooled across proteins without a justified common scale and estimand.

The [bootstrap documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html) explains paired resampling, but a numerical interval is not automatically reliable with ten repeated starts and a highly tied outcome. Any later intervals should state the resampled unit, statistic, method, seed, handling of degenerate samples and population to which the result can apply. Report per-protein paired observations and measurement counts regardless of whether an interval or test is defensible. Repeated starts can describe variation due to the sampling procedure on these fixed landscapes; they do not establish variation across proteins.

Recovery after a coverage warning has an additional missing-follow-up problem: a policy that stops before 30 later measurements cannot be assigned an observed recovery outcome. The [study findings](multiprotein_study_findings.md) already distinguish no warning, insufficient follow-up, recovery and no observed recovery. Do not replace unavailable follow-up with a zero or silently discard it from an estimate.

The best next analysis and its interpretation need a reviewed protocol before implementation. No p-values, confidence intervals or new scientific conclusions were produced in this review.
