# Ranking disagreement across candidate groups

Completed 16 November 2026 using the previously recorded ten amylase runs. This is an exploratory, retrospective analysis on one protein, not an independent evaluation of a warning. The procedure was documented in the [analysis plan](disagreement_context_plan.md) before these comparisons were run; the first-round top-versus-full results were already known when that plan was written.

## What the numbers mean

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

## Reconstruction and checks

The original compressed and uncompressed records, dataset and representation fingerprints, historical source files, model fitting membership, selected penalties and interval radii were checked by the existing replay. The extension checked every reconstructed candidate mean and spread against the saved pre-reveal record and checked all 100 top-group correlations against the prior warning replay. The previously reported first-round full and top values also matched. Every seed contributed ten rounds and five groups. The analysis uses scores only after their recorded reveal; no current-round hidden score or original split label is used for group selection or correlation.

The correlation implementation ranks ties and compares the resulting ranks; a test independently compares it with pairwise `scipy.stats.spearmanr`, including ties. Additional tests cover constant and invalid inputs. The full backend suite passed 27 tests. The per-round evidence, per-run descriptive summaries, replay records and input/code fingerprints are in [the output directory](../output/amylase_disagreement_context/).

Reproduction from the repository root, with the pinned representation cache and historical Git commit available:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend python3 scripts/analyze_disagreement_context.py output/amylase_ranges_repeated output/amylase_warning_replay_v2 NEW_OUTPUT_DIRECTORY
```

The command refuses to overwrite the output directory and produces the detailed correlation table and replay evidence. The committed per-run summary is calculated from that table. Further work needs an independently specified failure target and separate evaluation before changing the warning or claiming it improves decisions.
