<div align="center">

# Controlled warning simulations

Protocols and findings

</div>

## Coverage warning: protocol

The existing coverage warning fires when fewer than 75% of the last 30 newly measured scores fall inside their previously recorded prediction ranges: with 30 measurements this means at most 22 are covered. A warning is an observed window, whereas an underlying coverage probability is a property of a data-generating process. To evaluate the warning against known conditions, this development-only simulation supplies the underlying probability directly rather than inferring it from the same 30 observations.

Generate 1,000 independent 30-observation windows for each of three fixed coverage probabilities: 0.90 (nominal reference), 0.80 (moderate undercoverage relative to the 90% target), and 0.60 (severe undercoverage). Each observation is an independent yes/no draw with the stated fixed probability; use Python's seeded `random.Random(20261117)` and process the probabilities in the order above. The probabilities are illustrative assumptions, not estimates from any protein dataset and not tuned on IRED or Hydro. Label the 0.80 and 0.60 conditions as undercoverage and the 0.90 condition as reference before looking at generated results.

Apply the unchanged coverage-warning function to each generated history. Report triggered and not-triggered counts per condition, sensitivity separately for each undercoverage level, and false-alarm rate for the reference level. If reporting precision or F1, pair each undercoverage condition with the 1,000 reference windows and state that this artificial 50/50 mixture determines precision; it is not an estimate at the unknown prevalence of real failures. Preserve denominators and report unavailable statuses separately. Independently compare the observed trigger rates with exact binomial probabilities for at most 22 covered observations; [NIST's binomial reference](https://www.itl.nist.gov/div898/handbook/eda/section3/eda366i.htm) gives the probability model and its fixed-probability assumption.

This simulation probes the mathematical behavior of one existing rule under independent observations. Real sequential protein search deliberately selects observations using earlier data, which can invalidate that independence assumption; [Fannjiang et al.](https://pmc.ncbi.nlm.nih.gov/articles/PMC9618043/) discuss that dependence. The simulation does not establish warning accuracy on biological searches or validate the other four warning types. It does not change a threshold, model or dataset. The exact binomial probabilities for the 0.60 and 0.90 conditions were calculated as a feasibility check before this protocol was written; no protein-study outcomes were used to select these illustrative conditions.

## Coverage warning: findings

The [protocol](controlled_simulations.md#coverage-warning-protocol) generated 1,000 independent 30-observation windows at each of three known coverage probabilities, then applied the existing warning rule. The probabilities are illustrative synthetic conditions, not estimates from protein datasets. The warning fires when at most 22 of 30 observations are covered.

| Assumed coverage probability | Meaning in this simulation | Warnings | No warning | Exact warning probability under the independent model |
| ---: | --- | ---: | ---: | ---: |
| 90% | Nominal reference | 6/1,000 | 994/1,000 | 0.78% |
| 80% | Moderate undercoverage | 239/1,000 | 761/1,000 | 23.92% |
| 60% | Severe undercoverage | 946/1,000 | 54/1,000 | 95.65% |

Under this particular independent model, the rule is much more likely to flag severe undercoverage than a moderate drop from the 90% target. That is consistent with its lower trigger threshold and a 30-observation window; it is not evidence that real adaptive protein searches have these rates. The 90% case's 6/1,000 warning rate is a false-alarm rate only for this synthetic reference condition.

For an artificial mixture of 1,000 moderate-undercoverage windows and 1,000 nominal windows, the observed precision was 239/245 (97.6%), recall 239/1,000 (23.9%) and F1 about 0.384. For the corresponding severe-versus-nominal mixture, precision was 946/952 (99.4%), recall 946/1,000 (94.6%) and F1 about 0.969. These precision and F1 values depend on the chosen equal mixture and must not be treated as estimates for an unknown real-world prevalence. All 3,000 warnings had an available status.

The [simulation output](../../../output/warnings/coverage_warning_simulation.json) records the seed, conditions, counts, exact binomial probabilities, source fingerprints and software versions. The [audit output](../../../output/warnings/coverage_warning_simulation_audit.json) was captured directly from a separate reproducible audit. It regenerated all 3,000 windows without calling the warning function, independently checked the threshold and counts, and checked exact probabilities against SciPy's binomial calculation. It also rejects changed fingerprints or counts. The simulation output SHA-256 was `10383cf71f3dbd6e0a01b3966522e54466b173228c3389b9de2c500daa456aab`; the audit script SHA-256 was `b7c5afd952317e6d3955608781ccd68c6ab5d4c9cda6bd739931b913e5704380`. All 129 backend tests passed before the run.

The independent, fixed-probability assumption is deliberately simpler than the adaptive selection in CERA. This analysis does not validate the coverage warning on real protein searches, establish a biological failure rate, or evaluate the other warning types. No model, dataset, warning threshold or provider setting was changed.

## Model disagreement warning: protocol

The existing warning compares the rankings of five model members on up to 100 candidates. It triggers when the average of their ten pairwise Spearman correlations is below 0.5. A model member is one predictor in the group; Spearman correlation compares ordering, not the true measured score.

Construct 45 paired sets of ten synthetic candidates with a shared randomly permuted ranking, using `random.Random(2026111703)`. For each set generate three conditions: all five members have the same ranking; one member swaps a specific pair of ranks; or one member reverses the entire ordering. Enumerate all 45 pairs of ranks for the swap condition. The condition label comes from the deliberately planted ranking change, not from the warning output. All ten candidates are in the warning group, so no top-100 truncation occurs. Record the member predictions and warning status and value for every case.

For this experiment only, call a case positive if any model's order was deliberately changed, and negative if all five agree. Report warning counts and precision, recall, F1 and false-alarm rates separately for swapped versus identical and reversed versus identical cases, each using 45 positives and the same 45 negatives. The equal mixtures and extreme constructed patterns are not representative prevalence estimates; the 45 pairs are permutations of a small family of synthetic cases, not 45 proteins. An undefined precision or F1 denominator must be null rather than invented.

Independently reconstruct the planted permutations and calculate average pairwise rank correlations without calling the warning or its Spearman function. Compare each saved value, status, case and aggregate; fingerprint the code and environment. The [SciPy Spearman documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.spearmanr.html) describes rank correlation and undefined constant inputs. These deliberately distinct rankings are not true protein fitness labels: the experiment measures response to planted ranking differences, not whether models are correct or a repair is beneficial. Do not use results to tune the threshold.

## Model disagreement warning: findings

The [protocol](controlled_simulations.md#model-disagreement-warning-protocol) constructed 45 matched sets of ten synthetic candidates under each of three conditions: five identical model rankings, one model with a single rank-pair swap, and one model with a fully reversed ranking. The cases are permutations of a small family of constructed patterns, not independent proteins or experimental fitness measurements.

| Planted condition | Warnings | No warning | Average pairwise correlation range |
| --- | ---: | ---: | ---: |
| All identical | 0/45 | 45/45 | 1.000 |
| One model swaps two ranks | 0/45 | 45/45 | 0.607–0.995 |
| One model fully reversed | 45/45 | 0/45 | 0.200 |

The warning's existing threshold is an average pairwise correlation below 0.5. All single-swap cases were above that threshold; every constructed reversal was below it. If any planted ranking change is labeled positive, the swapped-versus-identical comparison has recall 0/45, zero false alarms among the 45 identical cases, undefined precision because no cases triggered, and F1 0. The reversed-versus-identical comparison has recall 45/45, precision 45/45, zero false alarms among 45 negatives and F1 1. These numbers describe deliberately chosen cases and an artificial equal mixture; they are not prevalence-adjusted or real-world accuracy estimates.

The [simulation output](../../../output/warnings/disagreement_warning_simulation.json) preserves all 135 planted member-prediction matrices, warning groups, values, statuses and code fingerprints. The separately captured [audit output](../../../output/warnings/disagreement_warning_simulation_audit.json) confirms that an independent rank calculation reconstructed all cases without calling the warning. Tests also check tied-rank arithmetic and rejection of altered member predictions. The simulation output SHA-256 was `87a8305747eebf0ccc862228c8f2381a7364df951f50f9e4c8eb1aa896586fa9`; the audit script SHA-256 was `2b561ae26f191ebf7653aa959bbe14a42b40ddbbfb278241951bb1e4890ec9a3`. All 133 backend tests passed before the run.

Disagreement among model members does not establish which model is right, whether the group prediction is wrong, or whether a repair improves a later search. The separate [Amylase ranking analysis](disagreement_ranking.md#findings) compares selected-batch predictions with subsequently measured scores but also does not establish warning accuracy on other proteins. No protein scores, model settings, warning thresholds or provider settings were changed in this simulation.

## Unfamiliar-candidate warning: protocol

The existing support warning requires at least three selected candidates to be farther than a threshold from previously known representations **and** have measured scores outside their recorded ranges. A representation is a list of numbers used to describe a sequence; this simulation uses one-number representations for transparent arithmetic, not protein embeddings.

Use five known points at 0, 1, 2, 3 and 4. Their nearest-other distances are all 1, making the existing threshold 1. Each batch contains ten distinct candidates. The reference condition places all candidates within 1 of a known point; both shifted conditions place every candidate more than 1 away. Shift labels are assigned from this construction before generating score misses, rather than from the warning's output. In the reference and well-covered shifted conditions each score independently misses its fixed range with probability 0.10; in the poorly covered shifted condition the miss probability is 0.50. A simulated inside score is 0.5 and a miss is 2.0, with range [0, 1]. The miss probabilities are illustrative, not estimated from protein data.

For each condition generate 1,000 independent batches with Python `random.Random(2026111702)`, in the order reference, shifted/well-covered, shifted/poorly-covered. Apply the existing distance snapshot and support warning. Report triggered, not-triggered and unavailable counts; treat shifted construction as positive and reference construction as negative for each separate 50/50 comparison. Report the resulting recall, false-alarm rate, precision and F1 with this artificial mixture explicitly stated. The reference condition cannot trigger the implemented rule by construction because none of its candidates is far, so its false-alarm result is structural and cannot estimate false alarms among other kinds of negative real-world cases.

For shifted batches all ten candidates are far, so the exact warning probability under the independent miss model is the probability of at least three misses in ten trials. Check this independently using the binomial distribution described by [NIST](https://www.itl.nist.gov/div898/handbook/eda/section3/eda366i.htm), and independently recompute distances, sampled miss counts and warning statuses. Capture software and source fingerprints. This probes whether the compound rule responds to a simple constructed shift; it does not prove that a warning detects biological distribution shift, that a miss was caused by unfamiliarity, or that real search observations are independent. No protein scores or warning thresholds are changed.

## Unfamiliar-candidate warning: findings

The [protocol](controlled_simulations.md#unfamiliar-candidate-warning-protocol) constructed one-dimensional near and far candidate batches with known independent score-miss probabilities. A shifted batch was defined by its constructed distances, independently of the warning result. This is a synthetic probe of the implemented compound rule, not a protein-data estimate or a claim that distance caused prediction misses.

| Constructed condition | Candidate distances | Per-score miss probability | Warnings | Exact warning probability under this independent model |
| --- | --- | ---: | ---: | ---: |
| Reference | All near | 10% | 0/1,000 | 0% by construction |
| Shifted, well covered | All far | 10% | 74/1,000 | 7.02% |
| Shifted, poorly covered | All far | 50% | 943/1,000 | 94.53% |

The warning requires at least three candidates to be both far and outside their ranges. In this constructed experiment, all far batches are labeled as shifted even if their scores remain inside the ranges. Therefore 926 well-covered shifted batches did not trigger; this is expected from the compound definition and should not be described as a general biological false-negative rate. The near reference cannot trigger by construction, so its zero false alarms do not estimate false alarms among other negative cases.

Using a separate artificial 50/50 mixture of 1,000 shifted and 1,000 reference batches for each comparison, observed recall was 7.4% for well-covered shifts and 94.3% for poorly covered shifts. Precision was 100% in both mixtures because the constructed reference condition cannot trigger; F1 was about 0.138 and 0.971, respectively. These values depend on the constructed cases and mixture, and do not measure real-world prevalence or accuracy.

The [simulation output](../../../output/warnings/support_warning_simulation.json) records the seed, distances, counts, exact binomial probabilities, versions and source fingerprints. A separate [reproducible audit](../../../output/warnings/support_warning_simulation_audit.json) regenerated all 3,000 batches without calling the warning, recomputed distances and trigger conditions, checked exact probabilities using SciPy, and rejected altered distances in testing. The simulation output SHA-256 was `7f745bfaea4372a7584877f08f74aa5a66f1ef0c0def429af91413fccb23e944`; the audit script SHA-256 was `df3ca8617b635a0a6ff174802a491344c76ea8178abab1802ce7d0bc1c93177d`. All 131 backend tests passed before this run. No protein scores, model thresholds or provider settings were changed.

## Constraint and diversity rules: protocol

This is a small set of hand-labeled software checks, not a biological detector study. It makes the existing boundary examples reproducible as a table of known inputs and warning outputs. The constraint cases use the reference `AAAAA`, a maximum of four changes, and explicit candidates. Ten cases include valid requests, a five-change sequence, a duplicate, an unknown identifier, an empty request, over-budget and over-batch requests, and a mixed request. The expected valid/invalid label is assigned by inspecting each constructed input, before applying the warning.

The diversity cases use five hand-labeled sequence batches. A batch is operationally positive when its mean number of differing sequence positions across pairs is strictly below two; exactly two is negative. One single-sequence batch has no pair and is labeled unavailable. These labels describe the warning's written rule, not an independent biological definition of harmful diversity loss. The other four cases have hand-calculated mean differences of 1, 2, 3 and 4/3.

Run the existing warning functions and record each input, assigned label and result. For the cases with known labels, report true and false alarms, misses, correct negatives, precision, recall, F1 and false-alarm rate; report the unavailable case separately. These ratios describe only these deliberately selected examples and cannot estimate real-world rates. A separate audit recomputes the input conditions and pair differences without calling the warning functions, checks case identities and fingerprints, and rejects altered results. The [ISTQB foundation syllabus](https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf) describes boundary-based software testing; it does not turn these selected examples into a representative biological sample. No protein score, search setting or threshold is changed.

## Constraint and diversity rules: findings

The [predeclared cases](controlled_simulations.md#constraint-and-diversity-rules-protocol) check whether the implementation follows its stated rules on selected inputs. They do **not** measure biological warning accuracy: the examples were selected by hand, and the diversity label uses the same sequence-difference rule as the warning rather than an independently observed harmful outcome.

| Warning | Positive cases caught | Negative cases correctly clear | Unavailable |
| --- | ---: | ---: | ---: |
| Constraint | 7 of 7 | 3 of 3 | 0 |
| Diversity | 2 of 2 | 2 of 2 | 1 |

For these small selected cases only, precision, recall and F1 are each 1 and the false-alarm fraction is 0. These numbers are not population estimates. The one-sequence batch is unavailable because no pair can be compared; it is excluded from the labeled calculations. The two-difference boundary was correctly clear because the rule triggers strictly below two.

The [case record](../../../output/warnings/rule_warning_controls.json) stores all inputs and outputs; the [separate audit](../../../output/warnings/rule_warning_controls_audit.json) independently recomputed each case and its counts. Reproduce with `PYTHONPATH=backend:. python3 -m scripts.repair.simulate_rule_warnings <new-output.json>` followed by `PYTHONPATH=backend:. python3 -m scripts.repair.audit_rule_warning_controls <new-output.json>`. Boundary examples are a standard way to check a rule's behavior at its limits ([ISTQB foundation syllabus, 2024](https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf)); classification metrics summarize agreement with specified labels, not whether those labels represent an independent biological failure ([scikit-learn documentation](https://scikit-learn.org/stable/modules/model_evaluation.html)).

## Controlled rule cases

The [test cases](../../../backend/tests/studies_warnings/test_controlled_warning_cases.py) use hand-labeled, invented sequences and requests. They exercise the current written rules without opening measured scores or modifying a search. This is implementation verification on constructed examples, not a representative experiment or an estimate of real-world error rates. Boundary testing exercises values on and immediately outside a rule's limit; the [ISTQB testing syllabus](https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf), published in 2024, describes the technique and its limits.

For constraints, the reference is `AAAAA` and at most four positions may differ. `CCCCA` differs at four positions and is allowed; `CCCCC` differs at five and is flagged. The ten cases also include an empty request, a repeated identifier, an unknown identifier, a mixed valid/invalid request, and requests at or over separate batch and remaining-budget limits. All ten expected statuses and reasons matched. The existing integration test separately confirms that a mixed valid/unknown request is rejected without consuming budget or recording a reveal. It does not establish that every possible invalid request is handled correctly.

For diversity, the check calculates how many positions differ for each pair in the selected batch, then averages those counts. `AAAA` and `AAAC` differ at one position and trigger the rule; `AAAA` and `AACC` differ at two and do not, because the rule is strictly below two. The three-sequence example `AAAA`, `AAAC`, `AACC` has pairwise differences 1, 2 and 1, averaging 4/3. All five hand-labeled examples matched, including one sequence for which the pairwise average is unavailable. These results confirm behavior on these examples, not that the threshold identifies a harmful biological loss of diversity.

The focused warning tests passed 11 tests and the full backend suite passed 105 tests on 2026-11-17. No protein labels, model thresholds or search behavior were changed. Independent event definitions and validation for the five warning types remain unfinished.
