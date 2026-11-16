# Experiment walkthrough and choices

Status: illustrative walkthrough; the primary candidate-pool choice is approved below, and the other experiment rules remain proposals. The variants and scores below are invented; they are not experimental results. The actual dataset facts and remaining questions are in the [evidence ledger](dataset_evidence_ledger.md).

## Who knows what?

Ravi wants to choose promising protein variants without spending too many measurements. The dataset is a table of protein sequences and previously measured scores. We simulate a lab by keeping most scores hidden from the search. A candidate is a variant that the search is allowed to choose. The controlled score holder has the full table; the search receives permitted sequences and only the measurements already revealed. A separate evaluator may use all scores after the run to compute agreed results. These are information roles, not yet implemented components.

The rule for constructing the starting set may depend on the benchmark's original train/test division. The selector should not be given score-derived division labels for unmeasured candidates: for Hydro, that label reveals which side of a score threshold the variant lies on. Using the division to construct the initial set is still an assumption based on prior score knowledge and must be disclosed.

## Two rounds

Suppose initial measurements A=4 and B=6 are already known. Four unmeasured candidates C, D, E and F are eligible. Their actual scores, shown here only for the explanation, are C=3, D=8, E=5 and F=7. Let the additional budget be two measurements, with one candidate selected per round.

1. **Before round one:** the search sees A and B's scores and candidate sequences. It does not see C through F's scores. It predicts C=9, D=7, E=5 and F=4, and chooses C. Record those predictions and that choice first.
2. **After round one:** the score holder reveals C=3. The search has used one of its two additional measurements. The stored prediction of 9 versus the revealed 3 is an observed mismatch. A warning might trigger under agreed rules, but this single mismatch does not establish its cause.
3. **Before round two:** the search can use A=4, B=6 and C=3 under the agreed fitting and checking rules. Suppose it predicts D=7, E=6, F=5 and chooses D. Again record the predictions and selection before revealing the score.
4. **After round two:** reveal D=8. The additional budget is exhausted. The best observed score is 8. A separate evaluator may calculate other agreed metrics using the full table without feeding hidden scores back into the search.

The proposal also needs explicit rules for a request that repeats C, an unknown candidate, a partially filled final batch and an empty candidate pool. Their behavior is not decided here.

## Choices requiring agreement

### Which candidates can be selected?

- **A. All eligible unqueried variants:** preserves the synopsis's proposed broad pool; the search may remain near starting examples instead of entering the intended shifted region. Report choices by original division after the run.
- **B. Shifted-side candidates only:** focuses on the target shift, but changes the search problem. For Hydro, membership itself corresponds to score information; the experimental consequences need explicit treatment.
- **C. Both as separate experiments:** makes the distinction visible but adds work and must not combine results as though they were one setting.

**Decision, 16 November 2026:** Varun chose A for the primary experiment. This does not define the eligibility constraints, approve the other rules, or guarantee that the search reaches the shifted side. Report selections by original division after the run. Option B remains unapproved as a separate study.

### How is the reference treated?

The reference is the starting protein sequence against which substitutions are counted. In amylase it appears in the local test side. Options include initially revealing its score, allowing it to be selected under the normal budget, or excluding it. Revealing it initially gives useful context but adds a starting measurement outside the proposed train-only selection; selecting it later preserves the ordinary query rule; excluding it changes the candidate pool. Specify whether any initial reference measurement counts toward the stated 100 starting measurements. No option is approved.

Recommendation for discussion: allow it to be selected like any other eligible unqueried variant; keep its score hidden until selected. The sequence can still serve as a reference for counting substitutions. This preserves the proposed train-side starting measurements without assuming that knowledge of a sequence includes knowledge of its measured score. The reference may never be selected, so comparisons requiring an initially measured reference would need a separate explicit rule.

### What does the budget count?

The synopsis proposes 100 starting measurements plus at most 100 new ones, in batches of ten. It does not by itself settle how duplicates, failed requests or an early stop are represented. Recommend recording initial and newly revealed counts separately and plotting outcomes against actual newly revealed measurements. The exact duplicate and failure rules remain open.

### Fair comparison

Each method should use the same starting examples, permitted candidate set, constraints and maximum number of new measurements. Different methods can make different choices. Record any differences in model fitting or computing cost so an improvement is not attributed to repairs without evidence. Early stopping is an outcome to record rather than silently filling in missing measurements.
