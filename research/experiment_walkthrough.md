# Experiment walkthrough and choices

Status: illustrative walkthrough. The variants and scores below are invented; they are not experimental results. Subsequent delegated development decisions are recorded in the [amylase development protocol](amylase_development_protocol.md); dataset facts and remaining questions are in the [evidence ledger](dataset_evidence_ledger.md).

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

The reference is the starting protein sequence against which substitutions are counted. In amylase it appears in the local test side. Options include initially revealing its score, allowing it to be selected under the normal budget, or excluding it. Revealing it initially gives useful context but adds a starting measurement outside the proposed train-only selection; selecting it later preserves the ordinary query rule; excluding it changes the candidate pool.

**Decision, 16 November 2026:** Varun chose to keep the amylase reference score hidden until the search selects it under the normal measurement budget. The reference sequence can still be used to count substitutions. The reference may never be selected. This decision does not determine reference treatment in other datasets or approve the starting-set rules.

### What does the budget count?

The synopsis proposes 100 starting measurements plus at most 100 new ones, in batches of ten. It does not by itself settle how duplicates, failed requests or an early stop are represented. Recommend recording initial and newly revealed counts separately and plotting outcomes against actual newly revealed measurements. The exact duplicate and failure rules remain open.

**Working choice, 16 November 2026:** Varun delegated the numerical choice after analysis. Retain 100 initial measurements and a maximum of 100 additional measurements for the main protocol as a provisional design, subject to dataset-specific feasibility checks and an amylase development pilot before the evaluation protocol is frozen. This follows the submitted synopsis, gives multiple opportunities for warnings and recovery, and permits paired comparisons; none of these facts proves it is optimal. The proposed 20% interval-setting subset would leave only 20 initial examples for setting intervals and 80 for model fitting, so interval stability and the allocation need investigation. Adaptive selection prevents assuming ordinary interval coverage guarantees. A smaller budget saves simulated measurements but provides fewer opportunities to observe recovery; a larger one offers more observations but reduces the low-budget character and increases workload. No pilot has been run and no optimality claim is made. Batch size, allocation of data roles, number of repeats and edge cases remain open.

Evidence: [FLIP2 benchmark](https://flip.protein.properties/) reports that split difficulty varies; [Fannjiang et al.](https://pmc.ncbi.nlm.nih.gov/articles/PMC9618043/) discuss uncertainty under selection based on earlier data; the [split-conformal rank formula](https://academic.oup.com/jrsssb/article/87/4/1100/8058684) shows the discrete dependence on the size of the interval-setting set. The 100/100 choice is a project design judgment, not a value established by those sources.

### How should the initial measurements be used?

The predictor learns from examples; a prediction interval is a range intended to cover a future measurement. In ordinary split-conformal prediction, a separate calibration set is used to set the range from previous prediction errors. The underlying predictor must not have been fit using those calibration scores. A range chosen using a set cannot be treated as independently verified merely because it covers the same set. The original benchmark's `validation` flag identifies a benchmark validation subset; it is not automatically a suitable calibration set for this new sequential experiment. [FLIP2 data format](https://flip.protein.properties/); [split-conformal reference](https://proceedings.mlr.press/v162/ndiaye22a.html).

Possible initial allocations of 100 known measurements:

- **80 to fit, 20 to set ranges:** matches the synopsis's 20% proposal; leaves more fitting data, but range setting relies on a small set. For a standard 90% split-conformal rank, 20 calibration errors select the 19th smallest error; that is a calculation, not a coverage guarantee for this adaptive search.
- **70 to fit, 30 to set ranges:** gives the range-setting step more examples, but reduces fitting data and departs from the synopsis's proposed fraction. It is not established to be better for CERA.
- **Reuse data through a more complex resampling method:** can make more data useful to fitting across multiple models, but needs a precisely specified method and its own validity analysis; it is not interchangeable with the synopsis's simple split.

Following Varun's delegation, the development pilot will begin with the synopsis's 80/20 allocation; the [development protocol](amylase_development_protocol.md) records how newly revealed scores are handled and its statistical limitations. No pilot has been implemented, and the allocation is not a proven optimum.

Local check, before any mutation cap or other exclusion: original validation flags have train/False, train/True and test/False counts respectively of 1,426/356/1,924 for amylase, 3,746/662/4,178 for IRED, and 9,974/2,493/12,468 for Hydro. These are available-row counts, not permission to reveal their scores or an approved selection method.

### Fair comparison

Each method should use the same starting examples, permitted candidate set, constraints and maximum number of new measurements. Different methods can make different choices. Record any differences in model fitting or computing cost so an improvement is not attributed to repairs without evidence. Early stopping is an outcome to record rather than silently filling in missing measurements.
