<div align="center">

# Four-protein matched search findings

Findings

</div>

The approved [protocol](design_and_runbook.md#comparison-protocol-draft) and [runbook](design_and_runbook.md#runbook-draft) specify ten starting seeds, nine methods, four separately analyzed proteins, 100 initial observations and at most 100 new measurements. Starting variants were sampled from all eligible sequences without using the benchmark split labels. All 360 runs reached a completed runner status; scientific early stops are reported below. These are retrospective searches over already measured variants, not new laboratory experiments, official FLIP2 benchmark scores or evidence that a method generalizes to other proteins.

## What the primary comparison showed

For each protein and seed, compare each repair method's best score at its actual stop with fixed reward at its own actual stop. Across 40 paired starting sets, both rule-based and Gemini-assisted repair had **0 higher, 35 equal and 5 lower** best scores than fixed reward. A tie is an absolute score difference at most 1e-12. Fixed reward used all 100 new measurements in every run; the rule-based method stopped after failed repairs in 35/40 runs, and the Gemini-assisted method in 36/40. The two repair methods' final best scores matched in all 40 pairs; in one pair Gemini stopped after ten fewer measurements. This does not establish method equivalence or imply that additional measurements would necessarily have helped.

| Protein | Fixed median new measurements | Rule-based median (range) | Gemini-assisted median (range) | Rule-based repairs accepted | Gemini-assisted repairs accepted |
| --- | ---: | ---: | ---: | ---: | ---: |
| IRED | 100 | 50 (20–100) | 50 (20–100) | 7 | 7 |
| Hydro P06241 | 100 | 55 (20–100) | 55 (20–90) | 10 | 10 |
| Hydro P01053 | 100 | 40 (30–70) | 40 (30–70) | 2 | 2 |
| Hydro P0A9X9 | 100 | 45 (20–100) | 45 (20–100) | 4 | 4 |

A repair was accepted when it passed the implemented local checks; that is not proof that it improved subsequent outcomes. The reported rule-change cost is a dimensionless menu-ordering score, not money or computing time. Per-attempt costs, warnings and actual stop reasons are in the [evaluation report](../../../output/multiprotein/four_protein/matched_eval_51_60_report.json).

In a descriptive comparison added after viewing the results, each repair policy had 0 higher, 39 tied and 1 lower best scores at equal measurement counts. All 30 Hydro starts tied for each policy. Nine IRED starts tied and one had a lower repair score. Four of each policy's five actual-stop losses became ties when fixed reward was read at the same count. For each protein and seed, the comparison takes the repair run's final best score and subtracts the fixed-reward best score at that run's measurement count. It uses the original absolute tie tolerance of 1e-12. The comparison is conditional on where repair stops, so it cannot isolate the effect of the repair itself. The [80 paired scores](../../../output/multiprotein/four_protein/matched_eval_51_60_same_measurements.json) include the source report's hash and scores at both fixed-reward comparison points.

The starting sets already contained a top-1% eligible variant in 9/10 IRED seeds, 8/10 P06241, 7/10 P01053 and 9/10 P0A9X9. That leaves limited room for the top-1% measure to distinguish methods. The highest score in the eligible measured pool is an evaluator-only reference, not a biological optimum.

## Other methods

The table gives the median of ten best scores at actual stop for each method. **Columns have different score scales and must not be compared numerically across proteins.** Finite-pool recombination and AdaLead-style search are adaptations constrained to the available measured variants; the expected-improvement method uses ensemble spread as an approximation.

| Method | IRED | Hydro P06241 | Hydro P01053 | Hydro P0A9X9 |
| --- | ---: | ---: | ---: | ---: |
| Random | 2.417525 | -0.273231 | 0.005498 | -1.531760 |
| Greedy prediction | 2.330071 | 0.010316 | 0.038189 | -1.574270 |
| Fixed reward | 2.330071 | 0.010316 | 0.038189 | -1.574270 |
| Rule-based repair | 2.330071 | 0.010316 | 0.038189 | -1.574270 |
| Gemini-assisted repair | 2.330071 | 0.010316 | 0.038189 | -1.574270 |
| Mean plus spread | 2.330071 | 0.010316 | 0.038189 | -1.574270 |
| Expected improvement | 2.330071 | 0.010316 | 0.038189 | -1.574270 |
| Finite-pool recombination | 2.409419 | 0.010316 | 0.038189 | -1.582270 |
| AdaLead-style search | 2.417525 | -0.225607 | 0.038189 | -1.574270 |

The medians conceal substantial ties, different starting scores, and unequal stopping budgets. AdaLead-style search stopped for lack of permitted neighbors in 9/10 IRED runs, 10/10 P06241, 10/10 P01053 and 7/10 P0A9X9. See the [method summary](../../../output/multiprotein/four_protein/matched_eval_51_60_method_summary.csv) and per-run report for actual counts, coverage and paired differences. These ten seeds reuse each protein's same measured dataset; they are not ten independent biological replications.

## Prediction ranges and recovery

Coverage is the proportion of measured scores inside prediction ranges recorded before measurement. Fixed-reward coverage was 940/1,000 on IRED, 952/1,000 on P06241, 684/1,000 on P01053 and 969/1,000 on P0A9X9. The P01053 observation is notably below the 90% target; adaptive selection and dependent measurements mean these counts are descriptive and do not establish a formal coverage guarantee. The [summary](../../../output/multiprotein/four_protein/matched_eval_51_60_method_summary.csv) includes range widths and denominators; random search has no predicted range.

The corresponding observed counts for the two repair policies over their **entire runs** are:

| Protein | Rule-based repair | Gemini-assisted repair |
| --- | ---: | ---: |
| IRED | 531/570 (93.2%) | 531/570 (93.2%) |
| Hydro P06241 | 530/560 (94.6%) | 521/550 (94.7%) |
| Hydro P01053 | 312/450 (69.3%) | 312/450 (69.3%) |
| Hydro P0A9X9 | 470/480 (97.9%) | 470/480 (97.9%) |

These counts aggregate ten starts per protein, but observations within and across runs are dependent and the policies often stopped at different times. They include measurements before an accepted repair, after it, and in runs without one. Thus they cannot be used as the synopsis's proposed **after-repair** coverage result or as evidence that a repair caused coverage to change. A separate one-off calculation re-read and verified both compressed and uncompressed fingerprints and recomputed coverage in all 80 repair-policy records; this check was not saved as a reusable audit.

For P01053 fixed reward, all ten runs had a coverage warning: two later reached the approved 26–28 of 30 recovery band and eight did not. Nine of ten runs in each repair arm had a warning but stopped with fewer than 30 later measurements; the remaining run had no coverage warning. Recovery is an observed later window, not evidence that the repair caused it. For the other three proteins, none of the fixed or repair runs had a coverage warning, even though other warnings could trigger repairs. The warning used by fixed reward and the targeted-disagreement warning used by repair are constructed from different candidate groups, so their counts should not be interpreted as a directly matched detector comparison.

## Gemini requests and costs

The 40 Gemini-assisted runs recorded 102 valid advice selections and four fallbacks, each associated with an HTTP 503 response. Their logged advice attempts reported 14,723 total tokens. The separate preflight request reported another 159 tokens and is not included in the study count. Rejected responses may lack usage metadata in the current client; the recorded total is not a complete billing total, and actual charges and account quota were not verified. The advisor received warning types and a sanitized menu rather than protein sequences or fitness scores. Gemini and rule-based arms have the same final best scores here; that is not proof that the hosted model made identical choices or adds no value in other conditions.

## Verification and limits

The independent audit checked all 360 run records, reconstructed 2,943 selection batches and 549 repair replays, and checked one available reward-distance round and two representative local-proposal rounds per protein. It checked repair menus, order, costs and target evidence. It did not independently refit every predictor, reproduce every distance or local proposal, or validate the scientific meaning of every warning and safeguard. The audit stdout counts were manually transcribed into [audit evidence](../../../output/multiprotein/four_protein/matched_eval_51_60_audit.json).

A separate one-off check independently read the source sequences and scores and verified all 360 summaries and 320 paired differences, including budgets, stopping, coverage, width, recovery windows, warnings, repair-cost entries and recorded provider accounting. This one-off check is not yet a reusable script. The full backend suite passed 97 tests before the study; the Gemini preflight was successful. Four fallbacks and the unresolved usage-accounting limitation remain material.

Data and reference identities, cache and code fingerprints, run statuses and compressed event records are in the four `output/multiprotein/four_protein/matched_eval_51_60_*` directories. The [evaluation report](../../../output/multiprotein/four_protein/matched_eval_51_60_report.json) retains per-run curves and summaries. IRED's split covers only a subset of screened variants, while the Hydro proteins have different scales and construct-provenance limitations described in their [preparation notes](../../data/ired_preparation.md) and [Hydro notes](../../data/hydro_preparation.md). These findings do not complete every proposed ablation, establish detector accuracy, or substitute for an independently designed external validation.
