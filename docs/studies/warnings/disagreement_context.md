<div align="center">

# Investigating the ranking-disagreement warning

Plan and findings

</div>

## Plan

Status: retrospective analysis completed; see [findings](disagreement_context.md#findings). The first-round comparison that motivated it was already inspected, so this is exploratory rather than independent confirmation.

### The question

The current warning compares the orderings from five predictors only among the 100 candidates with the highest average predicted scores. In ten first rounds, the average agreement was lower in this group than across the entire available pool. The warning fired in 98 of the 100 replayed rounds. Neither observation establishes that the warning identifies incorrect predictions.

Comparing only the top group with the whole pool mixes two differences: which candidates are included and how many are included. A fairer descriptive comparison also examines other groups of the same size. This does not by itself establish why agreement differs, or whether the warning helps make better decisions. Selecting a group using the same predictions whose agreement is examined can change the observed association; [Cole and colleagues (2010)](https://pmc.ncbi.nlm.nih.gov/articles/PMC2846442/) illustrate selection effects in a different setting, not this experiment specifically. Spearman correlation compares rankings, and is undefined for a constant input ([SciPy documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.spearmanr.html)).

### Proposed procedure

1. Reconstruct the existing ten amylase runs, seeds 2–11, and all ten rounds per run. Verify the recorded source, data and representation fingerprints, fitting identifiers, chosen model setting, saved range-setting radius, and reconstructed candidate predictions against the original records. Stop and report any mismatch. Reuse the existing replay and predictor code where practical; do not change the search or warning thresholds.
2. Before considering each round's newly revealed scores, order the eligible candidates by their recorded average prediction, with identifier as the tie-breaker. Compare five groups: the highest 100; the 100 centered in that ordering; the lowest 100; 100 drawn from the full pool using a recorded deterministic seed `4000 + 100 * run_seed + round_number`; and the entire pool. The random group can overlap the other groups. Report the actual candidate counts and fail clearly if fewer than 100 candidates are present in these historical runs.
3. For each group, calculate all ten pairwise Spearman correlations among the five members and their mean. Report a group as unavailable if any required correlation is undefined; do not drop pairs. Preserve the run, round, group, candidate count, sample seed, correlation and status in a table. No current-round hidden score or original train/test label is an input to the grouping or correlations. Update the known scores only after the historical reveal.
4. Check reconstructed top-group results against the existing warning replay and check correlation calculations independently on representative cases, including ties and a constant member. Confirm chronological use of known scores, group sizes, deterministic sampling and complete accounting of all 100 rounds. Preserve input and implementation fingerprints and list any failures rather than silently excluding them.
5. Report the per-round table and descriptive per-run summaries, with group differences and unavailable cases. Clearly identify the previously examined first rounds. Do not treat overlapping rounds or runs on one protein as independent biological replications, declare causation, tune a threshold, or claim warning accuracy. An independent definition of a prediction failure and a separate evaluation would be needed to assess whether any rule is useful.

### Design choices and limits

The equal-sized middle, bottom and random groups help distinguish a pattern specific to high-ranked candidates from one also seen in other slices. The full pool preserves the earlier comparison but differs in size. Random samples vary with their seed; one sample per round describes that sample and does not quantify sampling uncertainty. All these groups derive from the same historical dataset and predictor group. The comparison can motivate a future warning evaluation but cannot validate a warning or demonstrate a successful repair.

The existing top-group warning could instead be removed, retained unchanged, or revised. Removing it would avoid frequent alerts but discard a possible useful signal; retaining it keeps the originally specified condition but may create alert fatigue; changing it without an independently defined target risks fitting a rule to these runs. The recommended immediate step is to keep the existing warning unchanged while completing the descriptive comparison and then define a separate evaluation before deciding on a change.

## Findings

Completed 16 November 2026 using the previously recorded ten amylase runs. This is an exploratory, retrospective analysis on one protein, not an independent evaluation of a warning. The procedure was documented in the [analysis plan](disagreement_context.md#plan) before these comparisons were run; the first-round top-versus-full results were already known when that plan was written.

### What the numbers mean

Each of five predictors assigns a score to every eligible candidate. We compare their candidate orderings using Spearman correlation, then average the ten comparisons between pairs of predictors. A value near 1 means the orderings tend to agree; lower values mean less agreement. The value alone does not tell us which predictor is correct or whether the candidates will perform well. A constant ordering cannot be assigned a correlation and is recorded as unavailable. See the [SciPy reference](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.spearmanr.html).

The table averages the per-round correlation over 100 rounds. The top, middle, bottom and random groups each contain 100 candidates; the full group contains the entire available pool. Random samples may overlap the other groups.

| Candidate group | Mean correlation | Range across rounds |
| --- | ---: | ---: |
| Top 100 | 0.100 | -0.156 to 0.539 |
| Middle 100 | -0.221 | -0.238 to -0.168 |
| Bottom 100 | 0.221 | -0.143 to 0.740 |
| Random 100 | 0.644 | 0.204 to 0.896 |
| Full pool | 0.649 | 0.213 to 0.903 |

All 500 group-round correlations were available. Top-group agreement was lower than random-sample agreement and full-pool agreement in all 100 rounds, but **higher** than middle-group agreement in all 100 rounds. It was lower than bottom-group agreement in 72 rounds. The middle group is also selected by the same predictor averages, so this finding does not isolate a causal mechanism. Results vary by which group is examined and do not establish that low agreement is an error or that changing the warning would improve search.

The 100 rounds are dependent observations from ten runs on one dataset; the groups overlap, and a single seeded random sample per round does not measure sampling uncertainty. Neither these counts nor the warning triggers are false-alarm rates. No warning threshold or selection method was changed.

### Reconstruction and checks

The original compressed and uncompressed records, dataset and representation fingerprints, historical source files, model fitting membership, selected penalties and interval radii were checked by the existing replay. The extension checked every reconstructed candidate mean and spread against the saved pre-reveal record and checked all 100 top-group correlations against the prior warning replay. The previously reported first-round full and top values also matched. Every seed contributed ten rounds and five groups. The analysis uses scores only after their recorded reveal; no current-round hidden score or original split label is used for group selection or correlation.

The correlation implementation ranks ties and compares the resulting ranks; a test independently compares it with pairwise `scipy.stats.spearmanr`, including ties. Additional tests cover constant and invalid inputs. The full backend suite passed 27 tests. The per-round evidence, per-run descriptive summaries, replay records and input/code fingerprints are in [the output directory](../../../output/amylase/warnings/amylase_disagreement_context).

Reproduction from the repository root, with the pinned representation cache and historical Git commit available:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend:. python3 -m scripts.warnings.analyze_disagreement_context output/amylase/search/amylase_ranges_repeated output/amylase/warnings/amylase_warning_replay_v2 NEW_OUTPUT_DIRECTORY
```

The command refuses to overwrite the output directory and produces the detailed correlation table and replay evidence. The committed per-run summary is calculated from that table. Further work needs an independently specified failure target and separate evaluation before changing the warning or claiming it improves decisions.
