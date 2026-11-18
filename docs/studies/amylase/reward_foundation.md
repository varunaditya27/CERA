<div align="center">

# Reward foundation

Design and checks

</div>

## Reward specification and batch selection

Added 16 November 2026 as a development component. The reward is a recipe for ordering protein variants; it is not a laboratory measurement. The existing pilot still uses its original greedy prediction rule and has not been connected to this component.

### Decision and calculation

The [synopsis](../../college/Project_Synopsis.pdf) specifies predicted fitness minus weighted model spread and distance from known examples, plus a weighted diversity term. The specification shown there calls its weights placeholders. This implementation accepts those three named terms with the example ranges: 0–2 for each penalty and 0–1 for diversity. The trusted program fixes those bounds; a submitted specification cannot enlarge its own limits or add a new field. This follows the closed-object principle described by [JSON Schema](https://json-schema.org/understanding-json-schema/reference/object). The implementation is a direct Python validator, not a JSON Schema validator.

The development limits also reject more than four substitutions, more than ten rounds, more than ten selections per batch, and an abstention setting above two failed repairs. These are upper bounds, not claims that a particular setting is optimal. The caller remains responsible for enforcing the overall round count and repair stopping behavior. Hard constraints are applied as filters, so no finite penalty can override them.

For the diversity term, use the smallest number of differing positions between the candidate and any already chosen batch member, divided by sequence length; the first selected member gets zero. This makes the term between zero and one and encourages candidates unlike all prior batch choices. The synopsis does not specify this normalization or how to combine distances, so it is a provisional development decision, not a reproduced benchmark setting. Grouping candidates into a batch creates a trade-off between predicted value and diversity, as described in [Gentile et al. (2022)](https://proceedings.mlr.press/v162/gentile22a.html).

The selector expects a precomputed distance in [0, 1], model mean and nonnegative spread for each candidate and does not access any scores. A subsequent [reward pilot](reward_pilot.md) implements and checks a provisional distance normalization and connects the selector to an experiment. The mean and spread are in prediction units; no claim is made that the example weights are calibrated or comparable across datasets. Ties in reward are resolved by identifier, and selection stops at the smaller of the remaining measurement budget, batch size and eligible pool.

### Checks and limits

The backend suite passed 32 tests. New tests cover unknown fields, attempted range expansion, non-finite weights, boolean counts, constraints, score penalties, diversity, deterministic ties, partial and empty budgets, invalid features and duplicate sequences. A separate check passed the first historical amylase selection through the new selector with all weights set to zero: all ten choices matched the saved greedy choices among 3,175 eligible candidates. That one equivalence check is not an end-to-end repair experiment.

At this foundation step, the selector had not yet been connected to the pilot; that later integration is documented in [reward pilot findings](reward_pilot.md). No reward version history, repair menu, verification, rollback, abstention, language-model interface or evaluation of reward effectiveness was implemented by this step. The supported measurement interface is not a security boundary against direct access to source files.

## Selection performance

Completed 16 November 2026 before larger repeated comparisons. The batch-selection rule and hard constraints are unchanged. The implementation maintains each candidate's minimum normalized Hamming distance to selected sequences using NumPy arrays instead of recomputing every pair in Python. [NumPy's documentation](https://numpy.org/doc/stable/user/basics.broadcasting.html) describes array operations and notes that memory use must also be considered.

The optimized selector reproduced the saved selected identifiers and diversity values for all 12 fixed-reward and repair batches in the earlier matched seed-13 comparison. Saved reward values matched within `1e-14`. It also reproduced all six recorded repair-proposal replay selections. For the first batch, running the prior implementation obtained from Git and the new implementation on identical inputs produced exactly equal output. On this machine, the prior first batch took about 2.03 seconds; the new selector averaged about 0.115 seconds over the 12 saved batches. These are local observations, not a universal speed benchmark.

All 75 backend tests passed, including a separate small direct-calculation comparison and existing hard-constraint, tie and invalid-input checks. This is not an exhaustive proof of identical behavior for every possible floating-point input or every hardware platform; very close scores can be sensitive to numerical differences. The next comparisons must continue to save selections and scores for audit.
