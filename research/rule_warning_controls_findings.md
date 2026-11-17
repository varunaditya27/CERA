# Constraint and diversity rule controls

The [predeclared cases](rule_warning_controls_protocol.md) check whether the implementation follows its stated rules on selected inputs. They do **not** measure biological warning accuracy: the examples were selected by hand, and the diversity label uses the same sequence-difference rule as the warning rather than an independently observed harmful outcome.

| Warning | Positive cases caught | Negative cases correctly clear | Unavailable |
| --- | ---: | ---: | ---: |
| Constraint | 7 of 7 | 3 of 3 | 0 |
| Diversity | 2 of 2 | 2 of 2 | 1 |

For these small selected cases only, precision, recall and F1 are each 1 and the false-alarm fraction is 0. These numbers are not population estimates. The one-sequence batch is unavailable because no pair can be compared; it is excluded from the labeled calculations. The two-difference boundary was correctly clear because the rule triggers strictly below two.

The [case record](../output/rule_warning_controls.json) stores all inputs and outputs; the [separate audit](../output/rule_warning_controls_audit.json) independently recomputed each case and its counts. Reproduce with `PYTHONPATH=backend python3 scripts/simulate_rule_warnings.py <new-output.json>` followed by `PYTHONPATH=backend python3 scripts/audit_rule_warning_controls.py <new-output.json>`. Boundary examples are a standard way to check a rule's behavior at its limits ([ISTQB foundation syllabus, 2024](https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf)); classification metrics summarize agreement with specified labels, not whether those labels represent an independent biological failure ([scikit-learn documentation](https://scikit-learn.org/stable/modules/model_evaluation.html)).
