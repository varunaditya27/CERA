# Warning checks: development design

Status: development warning checks implemented after Varun's approval; see [warning-check findings](warning_checks_findings.md). Values below are development starting points from the submitted synopsis, not validated universal thresholds. The existing [range findings](repeated_range_findings.md) are exploratory. A warning indicates a condition worth investigating; it does not establish why an error occurred or whether a repair will help. Repairs remain unimplemented.

## A small example

Suppose Ravi's search records prediction ranges for a batch before revealing any scores. After revealing a score, ordinary program logic checks whether it is inside the saved range. Imagine that, over the latest 30 revealed scores, 22 are inside their previously saved ranges. The observed fraction is 22/30, or about 0.733. A proposed warning rule with a strict threshold of 0.75 would fire. If 23 of 30 were inside, it would not fire. These numbers are invented for explanation; the condition says nothing by itself about the reason for the misses.

## Common contract

- Save what the check is allowed to know at its own stage. Pre-reveal checks cannot see the current batch's hidden scores. Post-reveal checks use predictions, ranges and distances saved **before** those scores were revealed. Never pass original score-derived split membership to a selector or warning.
- Each result identifies the run and round, warning type, stage, status, input identifiers, measured quantity, threshold, and reason. Status is `triggered`, `not_triggered`, or `unavailable`. `unavailable` means a legitimate calculation cannot be made, such as fewer than 30 scores for a 30-score window or a constant ranking; it is not a passing result. Malformed or non-finite inputs are errors, not silent passes.
- Keep raw evidence in run records without duplicating hidden scores. Preserve input version, model and representation fingerprints, threshold method and units so another reader can reproduce the result. Do not use later results to alter earlier records.
- The synopsis lists an ordering for handling simultaneous warnings: constraint, support, coverage, disagreement, diversity. Record all observations first; this document does not implement prioritization of repairs or re-check semantics.
- For a controlled test, define an independent expected condition and verify it actually exists. Do not call a warning's own output its ground truth. If precision or recall has a zero denominator, report it as undefined. [Scikit-learn metric definitions](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.precision_recall_fscore_support.html).

## 1. Constraint violation

**When:** before revealing a proposed batch. A constraint is a rule that must be obeyed; the current amylase development rule allows at most four substitutions from its verified reference and only eligible, not-yet-revealed variants.

**Condition:** a proposed identifier is unknown, already revealed, duplicated, over budget, or a proposed sequence exceeds the agreed mutation cap. The measurement runner already rejects such requests. Keep the existing atomic rejection: do not reveal part of an invalid batch or spend its budget. Distinguish an invalid request from a discovered scientific failure.

**Checks:** valid batch; one invalid element among valid elements; exactly four versus five substitutions; duplicate; unknown or previously queried identifier; budget exhaustion. Inject invalid proposals only in isolated tests. An ordinary run with enforced filters is not evidence of how often the filter would fail if disabled.

## 2. Unfamiliar candidate plus missed range

**When:** compute distances and a threshold immediately before the batch is revealed; evaluate the joint warning only afterward, when the saved ranges can be compared with the newly revealed scores.

**Development definition:** represent each sequence by its existing 320-number ESM vector. Use raw Euclidean distance, a straight-line distance in that numerical space. For each candidate, find its nearest previously revealed sequence. To form the comparison distribution, for every previously revealed sequence find its nearest **other** previously revealed sequence; never include self-matches. Use the 90th percentile of those nearest-other distances, defined here as the value at rank `ceil(0.9 * n)` after sorting the `n` distances. Fire if at least three batch candidates have both a distance **strictly greater** than that threshold and a score outside their saved range. Equality with the range boundary counts as inside; equality with the distance threshold does not count as greater.

This raw-distance choice makes the units and percentile unambiguous for development. It is a working clarification of the synopsis's distance rule, not a validated threshold, and differs from its proposed distance normalization. Record this distinction before any formal experiment. Mutation count and representation-space distance are different quantities.

**Checks:** zero, two and three qualifying candidates; a far candidate inside its range; a near candidate outside its range; exact threshold and range-boundary ties; duplicate representations and zero nearest-other distances; fewer than two previously revealed sequences gives `unavailable`. A large distance plus a miss is an observed combination, not proof that distance caused the miss. Use the pre-batch known set rather than including the newly selected batch in its own reference set.

## 3. Low observed range coverage

**When:** after revealing a batch. Use the latest 30 newly revealed scores and their own pre-reveal ranges, even if a final batch is shorter than ten. The 100 starting scores do not have pre-reveal ranges and are not included.

**Condition:** fewer than 30 valid observations gives `unavailable`; otherwise fire when the fraction inside the last 30 ranges is **strictly below 0.75**. With 30 cases, 22/30 triggers and 23/30 does not. Record count, denominator and the relevant pre-reveal interval identifiers. The seven previously inspected overlapping windows are a post-hoc check of this rule, not evidence of a validated false-alarm rate.

**Checks:** 29 observations; 22/30 and 23/30; values exactly on a range boundary; a short last batch; chronological rolling-window ordering; missing or non-finite pre-reveal inputs. A single run or overlapping windows do not yield independent measurements of general reliability. The nominal 90% target is not a guarantee under this adaptive search. [Fannjiang et al.](https://pmc.ncbi.nlm.nih.gov/articles/PMC9618043/).

## 4. Model ranking disagreement

**When:** before revealing a batch. Rank candidates by the mean predicted score, using identifier as the deterministic tie-breaker; inspect up to the top 100 eligible unqueried candidates. Compute Spearman rank correlation for each of the ten pairs of the five members, then average the ten correlations. Spearman correlation compares ordering, with tied values receiving average ranks. A value near 1 means rankings tend to agree; lower values indicate less agreement, not automatically lower predictive accuracy.

**Condition:** fire when the mean is strictly below 0.5. If fewer than two candidates are available, or any required pair has a constant ranking or otherwise undefined correlation, return `unavailable` with the reason rather than counting it as agreement or dropping it silently. If fewer than 100 candidates remain but at least two have valid rankings, use all remaining candidates and record the actual count. [SciPy's Spearman documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.spearmanr.html) notes that constant inputs have undefined correlation.

**Implementation gap:** the current pilot logs only the group mean and standard deviation for each candidate. Those two numbers cannot reconstruct the five individual rankings. Existing runs can be reproduced from their recorded fitting data and member seeds, as was done in the prior audit; future real-time checks need the individual member predictions saved before reveal or independently reproducible pre-reveal evidence. Do not substitute the saved standard deviation for rank correlation.

**Checks:** identical ordering; opposite ordering; mixed pairs below and above 0.5; ties; constant member; fewer than two candidates; fewer than 100; deterministic top-rank ties and non-finite inputs.

## 5. Low batch diversity

**When:** after selecting a valid batch but before revealing scores. Diversity here means how different sequences in that particular batch are from one another.

**Condition:** compute the mean Hamming distance over all distinct pairs. Hamming distance is the number of differing positions in two equal-length sequences; for example `AAAA` and `AACA` have distance 1. Trigger if the mean is **strictly less than 2**. If the batch has fewer than two sequences, return `unavailable`. Unequal lengths are an invalid input, not a zero distance. This threshold is a starting rule, not proof that the batch is biologically inadequate.

**Checks:** three known sequences with manually calculated pair distances; mean just below, exactly at, and above 2; one sequence; duplicate proposals; unequal lengths. The ordinary runner rejects duplicates before this check; a duplicate case belongs in an isolated test.

## Implementation plan for approval

1. Implement the checks as focused backend modules with explicit inputs and statuses; preserve the existing measurement runner's behavior and hard rejections.
2. Save the individual member predictions, and the distance reference information needed for pre-reveal checks, before score revelation. Avoid hidden scores, score-derived split labels and unnecessary raw data in warning inputs. Record enough configuration and evidence for reproducibility.
3. Add deterministic tests for every positive, negative, boundary, unavailable and malformed case above. Verify failures do not bypass constraints or spend measurements. Test that warnings can be reconstructed from saved records and that old runner, comparison and range tests still pass.
4. Replay the defined checks against the existing amylase development records where their required evidence is available. Rebuild member predictions and distances from saved pre-reveal states if necessary, clearly labeling the analysis retrospective; otherwise report the missing evidence. Compare the existing coverage rule's output with the previously documented 7/80 post-hoc count. Do not report detector precision or false-alarm rates without independently defined ground truth.
5. Document outputs, incomplete cases and limitations, then commit. Leave repairs, language-model integration and final evaluation for later separately reviewed work.
