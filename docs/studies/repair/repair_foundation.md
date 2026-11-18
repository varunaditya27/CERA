<div align="center">

# Checked reward changes: development foundation

Design note

</div>

Implemented 16 November 2026. These functions are tested in isolation; they are not yet connected to the experiment runner, and no repair has been evaluated on a protein search. A checked change is not evidence of improved future performance.

## Why check a change?

A search can repeatedly favor candidates that look good to its prediction model but perform poorly when measured. Changing the ranking rule may make the search more cautious, but an arbitrary change can also make it worse. Model overestimation under a change in the candidate distribution is a known problem in offline optimization; [Trabucco et al. (2021)](https://proceedings.mlr.press/v139/trabucco21a.html) study a different conservative-model approach. The code here implements a small, testable part of the project's proposed repair process; it does not reproduce that paper's model or guarantees.

## Current finite menu

For a support-shift warning, propose raising the distance penalty. For coverage or disagreement, propose raising the uncertainty penalty. For low diversity, propose raising the diversity bonus. Each proposal increases the relevant weight by 0.25, 0.5 or 1.0, capped at its existing allowed maximum; duplicate and unchanged proposals are removed. A support warning is an observed combination of distance and a missed range, not proof that distance caused the miss. Constraint violations are not in the menu: they require rejecting the invalid selection and investigating the filter, not changing weights.

The cost is the weight change divided by that term's allowed range, plus 0.05 for changing one term. The increments, extra cost and mapping are provisional development decisions, not optimized values. Try lower-cost proposals first, with a deterministic weight tie-breaker. A proposal is considered only if it exactly matches this menu, preserving the goal, hard constraints, budget, all other terms and allowed ranges.

## Checks before acceptance

The caller must supply the candidate features and old reward as they were **before** the relevant batch was revealed, plus a nonempty list of warned-about identifiers that the old rule actually selected. The verifier replays that batch with the proposed reward and requires every listed identifier to be absent. This avoids a vacuous pass where the old rule would not have selected the supposedly problematic item. A warning about low diversity or model disagreement is not automatically an observed prediction error; its caller must state which selected items are being tested and why.

The verifier also requires:

1. The proposal matches the allowed menu and the selector still applies the unchanged hard constraints.
2. At least 20 supplied calibration observations have saved range bounds and scores; at least 80% must lie inside their bounds. The interval endpoints count as inside. This is a provisional tolerance around the nominal 90% target, not independent proof of 90% future coverage. The interval-setting data are reused, and adaptive selection can invalidate a conventional coverage guarantee; see [Fannjiang et al. (2022)](https://pmc.ncbi.nlm.nih.gov/articles/PMC9618043/).
3. At least five earlier measured examples have saved individual mean, spread, distance and score. The Spearman correlation between individual reward and score cannot fall by more than 0.05 relative to the old rule. This checks individual scores without the batch diversity bonus, which depends on the other selected variants. A constant ranking, constant scores, insufficient data or otherwise undefined correlation makes this check unavailable and the proposal is not accepted; [SciPy's documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.spearmanr.html) describes the undefined constant case.

Coverage is calculated on the supplied saved ranges, which a weight change does not alter. A pass therefore does **not** show that increasing an uncertainty penalty repairs coverage. Similarly, the ranking check uses previously revealed evidence and may be biased or noisy. The caller is responsible for proving that all supplied measurements were available at the relevant stage and that the candidate snapshot is genuine; this standalone verifier cannot establish chronology on its own.

The chooser returns the first proposal that passes all checks. If none passes, it returns an unchanged copy of the old rule and an audit of all attempts. It does not yet count consecutive failed repairs, implement abstention, invoke Gemini, prioritize simultaneous warnings or re-check warnings after an accepted change.

## Verification performed

The full backend suite passed 46 tests. New controlled examples verify that the cheapest valid proposal can displace a selected example and pass all checks; insufficient calibration, constant rankings, changed constraints, retained counterexamples, low coverage, rank deterioration, invalid measurements and an exhausted menu cannot produce a false acceptance. These examples establish behavior on constructed inputs, not detector accuracy, repair effectiveness or a completed end-to-end episode.
