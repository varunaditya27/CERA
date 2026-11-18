<div align="center">

# Coverage after the first accepted repair

Findings

</div>

This exploratory, post-result analysis follows the [additional metrics protocol](../multiprotein/additional_metrics.md#protocol). A repair is accepted when it passes the implemented checks; that does not establish later benefit. For each repair-policy run, examine the first 30 new measurements after its first accepted repair and count how many fall inside ranges saved before those measurements were revealed. The 26–28 of 30 band corresponds to the previously approved 90% target within five percentage points. A count above 28 is outside this band too; it does not by itself establish a harmful interval.

| Study / protein | Repair policy | No accepted repair | Fewer than 30 later measurements | Complete windows | Complete windows in 26–28 band |
| --- | --- | ---: | ---: | ---: | ---: |
| Four-protein IRED | Rule-based | 5 | 0 | 5 | 2 |
| Four-protein IRED | Gemini-assisted | 5 | 0 | 5 | 1 |
| Hydro P06241 | Rule-based | 3 | 1 | 6 | 1 |
| Hydro P06241 | Gemini-assisted | 3 | 1 | 6 | 1 |
| Hydro P01053 | Rule-based | 8 | 0 | 2 | 0 |
| Hydro P01053 | Gemini-assisted | 8 | 0 | 2 | 0 |
| Hydro P0A9X9 | Rule-based | 7 | 0 | 3 | 2 |
| Hydro P0A9X9 | Gemini-assisted | 7 | 0 | 3 | 2 |
| IRED low-change start | Rule-based | 5 | 2 | 3 | 1 |
| IRED low-change start | Gemini-assisted | 5 | 2 | 3 | 1 |

There are ten runs per row. Across these 100 policy runs, 56 had no accepted repair, six had insufficient later measurements, and 38 had a complete window. These are repeated starts on the same protein datasets, and the two repair policies are paired, so the counts are not 100 independent biological trials. Other repairs can occur during a later window, and the search chooses variants adaptively. Consequently these results neither prove that a repair caused the later coverage nor establish that the original proposal's target was met on its proposed official shift splits.

The complete per-run records, including the measurement at which the first repair was accepted and the number of later measurements, are in [four-protein after-repair metrics](../../../output/multiprotein/four_protein/matched_eval_51_60_after_repair_metrics.json) and [IRED low-change after-repair metrics](../../../output/multiprotein/ired_low_change/ired_low_change_61_70_after_repair_metrics.json). They supersede the earlier additional-metrics files for the same descriptive fields while adding after-repair results. Their SHA-256 values are `b2070c9dc3db07072fb977816ccfe4a326c3ae8a8686d83b626c20e91d1730bf` and `ca11bf4de44a05f5e2c07646764479ef76cbc193999c62a51ae09e9f07a48b0e`, respectively.

A separate one-off calculation checked the first accepted action, subsequent measurement count and first-window coverage against all 100 compressed repair records, and verified that the previously reported metric fields were unchanged. This check was not saved as a reusable audit. All 119 backend tests passed before the calculation; no new search or provider call was made.
