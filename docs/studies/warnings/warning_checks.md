<div align="center">

# Warning checks

Design and findings

</div>

## Design

Status: development warning checks implemented after Varun's approval; see [warning-check findings](warning_checks.md#findings). Values below are development starting points from the submitted synopsis, not validated universal thresholds. The existing [range findings](../amylase/repeated_ranges.md#findings) are exploratory. A warning indicates a condition worth investigating; it does not establish why an error occurred or whether a repair will help. Repairs remain unimplemented.

### A small example

Suppose Ravi's search records prediction ranges for a batch before revealing any scores. After revealing a score, ordinary program logic checks whether it is inside the saved range. Imagine that, over the latest 30 revealed scores, 22 are inside their previously saved ranges. The observed fraction is 22/30, or about 0.733. A proposed warning rule with a strict threshold of 0.75 would fire. If 23 of 30 were inside, it would not fire. These numbers are invented for explanation; the condition says nothing by itself about the reason for the misses.

### Common contract

- Save what the check is allowed to know at its own stage. Pre-reveal checks cannot see the current batch's hidden scores. Post-reveal checks use predictions, ranges and distances saved **before** those scores were revealed. Never pass original score-derived split membership to a selector or warning.
- Each result identifies the run and round, warning type, stage, status, input identifiers, measured quantity, threshold, and reason. Status is `triggered`, `not_triggered`, or `unavailable`. `unavailable` means a legitimate calculation cannot be made, such as fewer than 30 scores for a 30-score window or a constant ranking; it is not a passing result. Malformed or non-finite inputs are errors, not silent passes.
- Keep raw evidence in run records without duplicating hidden scores. Preserve input version, model and representation fingerprints, threshold method and units so another reader can reproduce the result. Do not use later results to alter earlier records.
- The synopsis lists an ordering for handling simultaneous warnings: constraint, support, coverage, disagreement, diversity. Record all observations first; this document does not implement prioritization of repairs or re-check semantics.
- For a controlled test, define an independent expected condition and verify it actually exists. Do not call a warning's own output its ground truth. If precision or recall has a zero denominator, report it as undefined. [Scikit-learn metric definitions](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.precision_recall_fscore_support.html).

### 1. Constraint violation

**When:** before revealing a proposed batch. A constraint is a rule that must be obeyed; the current amylase development rule allows at most four substitutions from its verified reference and only eligible, not-yet-revealed variants.

**Condition:** a proposed identifier is unknown, already revealed, duplicated, over budget, or a proposed sequence exceeds the agreed mutation cap. The measurement runner already rejects such requests. Keep the existing atomic rejection: do not reveal part of an invalid batch or spend its budget. Distinguish an invalid request from a discovered scientific failure.

**Checks:** valid batch; one invalid element among valid elements; exactly four versus five substitutions; duplicate; unknown or previously queried identifier; budget exhaustion. Inject invalid proposals only in isolated tests. An ordinary run with enforced filters is not evidence of how often the filter would fail if disabled.

### 2. Unfamiliar candidate plus missed range

**When:** compute distances and a threshold immediately before the batch is revealed; evaluate the joint warning only afterward, when the saved ranges can be compared with the newly revealed scores.

**Development definition:** represent each sequence by its existing 320-number ESM vector. Use raw Euclidean distance, a straight-line distance in that numerical space. For each candidate, find its nearest previously revealed sequence. To form the comparison distribution, for every previously revealed sequence find its nearest **other** previously revealed sequence; never include self-matches. Use the 90th percentile of those nearest-other distances, defined here as the value at rank `ceil(0.9 * n)` after sorting the `n` distances. Fire if at least three batch candidates have both a distance **strictly greater** than that threshold and a score outside their saved range. Equality with the range boundary counts as inside; equality with the distance threshold does not count as greater.

This raw-distance choice makes the units and percentile unambiguous for development. It is a working clarification of the synopsis's distance rule, not a validated threshold, and differs from its proposed distance normalization. Record this distinction before any formal experiment. Mutation count and representation-space distance are different quantities.

**Checks:** zero, two and three qualifying candidates; a far candidate inside its range; a near candidate outside its range; exact threshold and range-boundary ties; duplicate representations and zero nearest-other distances; fewer than two previously revealed sequences gives `unavailable`. A large distance plus a miss is an observed combination, not proof that distance caused the miss. Use the pre-batch known set rather than including the newly selected batch in its own reference set.

### 3. Low observed range coverage

**When:** after revealing a batch. Use the latest 30 newly revealed scores and their own pre-reveal ranges, even if a final batch is shorter than ten. The 100 starting scores do not have pre-reveal ranges and are not included.

**Condition:** fewer than 30 valid observations gives `unavailable`; otherwise fire when the fraction inside the last 30 ranges is **strictly below 0.75**. With 30 cases, 22/30 triggers and 23/30 does not. Record count, denominator and the relevant pre-reveal interval identifiers. The seven previously inspected overlapping windows are a post-hoc check of this rule, not evidence of a validated false-alarm rate.

**Checks:** 29 observations; 22/30 and 23/30; values exactly on a range boundary; a short last batch; chronological rolling-window ordering; missing or non-finite pre-reveal inputs. A single run or overlapping windows do not yield independent measurements of general reliability. The nominal 90% target is not a guarantee under this adaptive search. [Fannjiang et al.](https://pmc.ncbi.nlm.nih.gov/articles/PMC9618043/).

### 4. Model ranking disagreement

**When:** before revealing a batch. Rank candidates by the mean predicted score, using identifier as the deterministic tie-breaker; inspect up to the top 100 eligible unqueried candidates. Compute Spearman rank correlation for each of the ten pairs of the five members, then average the ten correlations. Spearman correlation compares ordering, with tied values receiving average ranks. A value near 1 means rankings tend to agree; lower values indicate less agreement, not automatically lower predictive accuracy.

**Condition:** fire when the mean is strictly below 0.5. If fewer than two candidates are available, or any required pair has a constant ranking or otherwise undefined correlation, return `unavailable` with the reason rather than counting it as agreement or dropping it silently. If fewer than 100 candidates remain but at least two have valid rankings, use all remaining candidates and record the actual count. [SciPy's Spearman documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.spearmanr.html) notes that constant inputs have undefined correlation.

**Implementation gap:** the current pilot logs only the group mean and standard deviation for each candidate. Those two numbers cannot reconstruct the five individual rankings. Existing runs can be reproduced from their recorded fitting data and member seeds, as was done in the prior audit; future real-time checks need the individual member predictions saved before reveal or independently reproducible pre-reveal evidence. Do not substitute the saved standard deviation for rank correlation.

**Checks:** identical ordering; opposite ordering; mixed pairs below and above 0.5; ties; constant member; fewer than two candidates; fewer than 100; deterministic top-rank ties and non-finite inputs.

### 5. Low batch diversity

**When:** after selecting a valid batch but before revealing scores. Diversity here means how different sequences in that particular batch are from one another.

**Condition:** compute the mean Hamming distance over all distinct pairs. Hamming distance is the number of differing positions in two equal-length sequences; for example `AAAA` and `AACA` have distance 1. Trigger if the mean is **strictly less than 2**. If the batch has fewer than two sequences, return `unavailable`. Unequal lengths are an invalid input, not a zero distance. This threshold is a starting rule, not proof that the batch is biologically inadequate.

**Checks:** three known sequences with manually calculated pair distances; mean just below, exactly at, and above 2; one sequence; duplicate proposals; unequal lengths. The ordinary runner rejects duplicates before this check; a duplicate case belongs in an isolated test.

### Implementation plan for approval

1. Implement the checks as focused backend modules with explicit inputs and statuses; preserve the existing measurement runner's behavior and hard rejections.
2. Save the individual member predictions, and the distance reference information needed for pre-reveal checks, before score revelation. Avoid hidden scores, score-derived split labels and unnecessary raw data in warning inputs. Record enough configuration and evidence for reproducibility.
3. Add deterministic tests for every positive, negative, boundary, unavailable and malformed case above. Verify failures do not bypass constraints or spend measurements. Test that warnings can be reconstructed from saved records and that old runner, comparison and range tests still pass.
4. Replay the defined checks against the existing amylase development records where their required evidence is available. Rebuild member predictions and distances from saved pre-reveal states if necessary, clearly labeling the analysis retrospective; otherwise report the missing evidence. Compare the existing coverage rule's output with the previously documented 7/80 post-hoc count. Do not report detector precision or false-alarm rates without independently defined ground truth.
5. Document outputs, incomplete cases and limitations, then commit. Leave repairs, language-model integration and final evaluation for later separately reviewed work.

## Findings

Implemented and checked 16 November 2026 under the [warning design](warning_checks.md#design). These warning rules are development thresholds, not validated diagnoses, error rates or evidence that a repair would work. The retrospective replay and fresh pilot are not final evaluations.

### What was implemented

The five checks cover invalid requests, unfamiliar candidates that also miss a prediction range, low observed range coverage, disagreement among individual predictor rankings, and low sequence diversity within a batch. Each emits `triggered`, `not_triggered`, or `unavailable`. Invalid inputs raise errors. Existing measurement-runner checks still reject invalid batches without revealing any scores or spending budget.

For new runs, individual member predictions for the top candidates and the nearest-known-distance snapshot are recorded before scores are revealed. Support and rolling-coverage checks are recorded afterward. The distance threshold uses raw Euclidean distance to the nearest *other* known representation, with the 90th percentile defined in the design; this remains a provisional clarification of the synopsis's normalized-distance wording, not a validated threshold.

The separate historical replay reads the ten previously saved range-pilot records, verifies their compressed and uncompressed fingerprints, checks their original source fingerprints against Git commit `78fce61`, and rebuilds the historical predictor group before computing warnings. It verifies the reconstructed top predictions and range-setting radius against each historical record. Original records are never modified; a replay log refers back to its input record and records pre- and post-reveal evidence in chronological order. Full original Git history including that commit is needed for this replay.

### Retrospective replay results

Across the ten previous runs and 100 batches:

| Warning | Triggered | Not triggered | Unavailable |
| --- | ---: | ---: | ---: |
| Constraint | 0 | 100 | 0 |
| Unfamiliar candidate plus range miss | 6 | 94 | 0 |
| Low range coverage | 7 | 73 | 20 |
| Member ranking disagreement | 98 | 2 | 0 |
| Low batch diversity | 0 | 100 | 0 |

Coverage is unavailable in the first two batches of each run because 30 newly revealed scores are required. The seven low-coverage results match the earlier post-hoc inspection. These are counts of overlapping batches from ten runs on one dataset, not precision, recall, false-alarm rate or independent biological replication. In particular, no actual constraint violation is expected when the hard filter rejects invalid requests first.

The 98 disagreement warnings make the current threshold worth investigating. In a **post-hoc** first-round analysis of the same ten reconstructed models, mean pairwise ranking correlation averaged about 0.737 across the full candidate pools and about 0.265 among only each round's top 100 candidates. The two calculations concern different candidate groups, and top candidates are selected by the same models. This shows that the warning depends strongly on the evaluation group; it does not prove why or whether a warning is useful. Per-seed values are in [first_round_rank_context.csv](../../../output/amylase/warnings/amylase_warning_replay_v2/first_round_rank_context.csv).

The final replay evidence and per-seed warning counts are in [amylase_warning_replay_v2](../../../output/amylase/warnings/amylase_warning_replay_v2). The preceding working replay was independently audited before the final replay added stricter input and source checks; the ten final warning evidence files were checked to match that audit, aside from replay metadata.

### Fresh run and verification

One fresh seed-12 pilot recorded 10 batches and pre-reveal warning evidence. Ranking disagreement triggered in all ten batches. Constraint, diversity and unfamiliar-candidate-plus-miss warnings did not trigger. The coverage warning was unavailable for the first two batches and did not trigger in the remaining eight. The pilot's saved ranges covered 99 of its 100 selected scores. These observations are one development run, not evidence of a warning's false-alarm rate.

An independent audit of the fresh record checked event order, source fingerprints, selected identities and scores, budget, mutation limits, coverage history, Hamming diversity, ranking correlation calculated independently from saved member predictions, and distances recalculated from the saved pre-reveal known sets. The same independent calculations were checked on all 100 historical replay batches. The live coverage table was reconstructed from the run record even with warning events present.

Unit tests cover positive and negative examples, strict boundaries, duplicates, invalid data, unavailable cases, ranking ties, zero-distance representations, atomic invalid-batch rejection and reconstruction of a post-reveal warning from saved pre-reveal evidence. No model thresholds were tuned as a result of the replay.

### Limitations

No independently defined ground-truth dataset of warning events has been established, so precision and recall have not been measured. Correlations can be undefined for constant rankings; such cases are reported unavailable. Recorded warnings are not inferred causes and are not repairs. The current predictor group contains five ridge models, not the complete predictor mixture proposed in the synopsis. Neither warning priorities, repair selection, language-model involvement nor recovery after a repair is implemented.
