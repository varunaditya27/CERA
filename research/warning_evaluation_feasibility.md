# Warning evaluation: feasibility and design questions

Status: read-only design review, 2026-11-17. No thresholds, experiments or implementation are approved by this document. This concerns the Amylase development landscape only; do not use IRED or Hydro outcomes to choose the definitions.

A warning is a signal, not proof of a failure. To evaluate one, choose the event it is supposed to identify, label that event without using the warning's own answer, and compare both for the same cases. A true alarm is a warning with the event; a false alarm is a warning without it; a miss is an event without a warning. Precision is true alarms divided by all alarms, and recall is true alarms divided by all events. If a denominator is zero, its rate is undefined, not zero. The [metric definitions](https://scikit-learn.org/stable/auto_examples/model_selection/plot_precision_recall.html) explain these distinctions.

## What can be established

| Existing check | Independent reference or outcome to investigate | What it can and cannot establish |
| --- | --- | --- |
| Invalid batch | A separately implemented, independently checked list of actual violations in deliberately constructed proposals: over the mutation limit, duplicate, unknown, or over budget. Include valid proposals matched to each kind. | Agreement tests detection of explicit rule violations on those examples. It does not estimate how often invalid proposals arise during normal operation, where the existing runner rejects them. Do not reveal scores for invalid proposals. |
| Unfamiliar candidates plus missed ranges | Independently label a later prediction failure using predictions frozen before later measurements and a definition that does not reuse the same batch's distance-and-miss rule. | This can assess whether a warning precedes that specifically defined later outcome; it cannot establish that unfamiliarity caused it. Some runs may have too little follow-up. |
| Low coverage | Use a disjoint later window of predictions frozen before their scores were revealed; define the later coverage event and window length before analysis. | This assesses prediction of a later window's observed misses, not the true long-run coverage probability or the cause of an earlier warning. A later window unavailable before stopping must be counted separately. |
| Disagreement among model rankings | Compare the saved warning with a separately specified later ranking-error outcome, using saved predictions and subsequently revealed measurements. | Only selected variants have prospective scores in ordinary records; selective measurement may bias the result, and small batches and ties can make ranking undefined. Do not treat disagreement itself as the independent error label. |
| Low sequence diversity | Independently recompute the stated within-batch sequence-difference rule for constructed batches; explore whether a separately justified later outcome can be observed. | The first comparison checks implementation of the definition, not whether a biologically harmful diversity collapse occurred. The available fitness data alone do not identify such harm without an additional defensible outcome and comparison. |

Existing tests in `backend/tests/test_warning_checks.py` exercise boundaries and unavailable cases; the [development findings](warning_checks_findings.md) report replay counts, not detector accuracy. In particular, injecting a small calibration set or removing a selection rule changes a setup but does not prove that a particular failure happened.

## Candidate study design for review

1. Inventory the development records for saved pre-reveal predictions, warning timing, selected identifiers, later outcomes, run ends and source fingerprints. Report missing evidence before calculating any rate. Use original source files and commits to verify records.
2. For each question, write the unit being counted, independent outcome, earliest permitted observation time, follow-up length, handling of ties and unavailable outcomes, and the population of runs. Freeze these before looking at the corresponding evaluation outcomes. Preserve a separate development/evaluation boundary if definitions are selected from development observations; otherwise label the result exploratory.
3. For constructed invalid batches, verify reference labels by hand on small examples and independent calculation on larger examples. For other warnings, compare alarm status against a later, disjoint outcome when available. Keep warning-unavailable and outcome-unavailable counts explicit; never silently turn them into negative cases. Report raw counts and denominators alongside any rates.
4. Treat consecutive windows and repeated batches in the same run as dependent. Report per-run as well as overall counts; do not pretend each overlapping window is an independent protein. Specify uncertainty methods only after deciding the unit and available sample size.
5. Where records cannot support a defensible outcome, report that warning's accuracy as unestablished. No comparison here would prove that a repair caused an improvement.

The 2022 [Fannjiang et al. paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC9618043/) explains that choosing future protein sequences using the fitted model makes later data dependent on earlier data. It motivates checking observed coverage carefully; its method and guarantees do not automatically apply to this project's existing intervals.

## Decisions still needed

The later outcomes and window sizes above are candidates, not established ground truth. Their scientific meaning, prevalence, amount of follow-up and sensitivity to selection must be checked before choosing them. Separate agreement with a specified rule from usefulness in anticipating a later problem. Any new code, generated cases or runs require a reviewed plan under the project's working rules.
