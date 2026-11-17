# Matched mixed-predictor search comparison

Twenty Amylase searches completed under the [protocol](mixed_search_comparison_protocol.md): ten matched starts, with either the mixed predictor or five ridge members, no reward repair, and 100 new measurements each. Both methods ended with the same best observed score in all ten pairs. In four pairs both improved on the best initial score; in six pairs neither did. A tie in the best score does not mean the selections or complete score histories were identical, nor does it prove the methods equivalent.

| Measure | Mixed group | Five-ridge group |
| --- | ---: | ---: |
| Final best score: higher / tied / lower across ten pairs | 0 / 10 / 0 | 0 / 10 / 0 |
| Selected scores inside prediction ranges | 878 / 1,000 | 842 / 1,000 |
| Mean range width | 0.16530 | 0.16371 |
| Mean episode elapsed time | 5.32 seconds | 2.56 seconds |

Coverage is descriptive: the methods chose different variants, and the selected observations do not provide a controlled coverage comparison. Elapsed times are from this machine and include the full episode, not just training; they are not synchronized GPU microbenchmarks or portable performance estimates.

The [audit result](../output/mixed_search_comparison_191_200_audit.json) contains the per-run scores and source-record fingerprints. Its replay checked matching initial examples and range-setting roles, all 200 selections, revealed source scores, range summaries and the full budgets. The mixed-predictor audit independently refitted the first predictor group for each run on the same GPU and reproduced its recorded first-round predictions. It did not independently refit all later groups, and it does not establish scientific validity of warnings. The compressed records and process logs are in [the output directory](../output/mixed_search_comparison_191_200/). Re-run the audit with a new output path:

```sh
TORCH_DISABLE_NATIVE_JIT=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend python3 scripts/audit_mixed_search_comparison.py output/mixed_search_comparison_191_200 research/reward_spec_example.json output/my-mixed-search-audit.json
```

This comparison is exploratory and retrospective. The ten starts reuse one development dataset already examined during the project, and the result does not measure reward repair, performance on other proteins, or new laboratory outcomes. It is not a confirmatory test or evidence of model equivalence. The [separate exported-model comparison](exported_model_evaluation_findings.md) answers a different, static prediction question.
