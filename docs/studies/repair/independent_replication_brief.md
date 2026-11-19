<div align="center">

# Independent replication brief

What another group needs to test the repair question with their own code

</div>

The [repair-without-stopping study](repair_without_stopping.md) was run by the same people and code that built the method, so it tests repeatability, not the idea. A group that implements the question separately would test whether the finding survives different code.

## Question

When a search detects a warning and changes its scoring rule, does the early stop that follows failed repairs, rather than the changed rule, explain why repair scored below a fixed scoring rule?

## What to build

A protein-variant search that, from the same starting measurements and a budget of 100 new measurements in ten batches of ten, can run in three modes: a fixed scoring rule; the same rule with checked changes after warnings and an early stop after repeated failed changes; and the same repair without the early stop. The scoring rule combines predicted fitness, a penalty for model disagreement, a penalty for distance from known variants and a bonus for batch diversity. The exact specification is `configs/reward_spec_example.json`; the warnings, repair menu and checks are described in [warning checks](../warnings/warning_checks.md), [repair foundation](repair_foundation.md) and the [glossary](../../glossary.md).

## Data and starts

IRED low-change starts and the three Hydro proteins with low-fitness starts, from `data/raw/flip2/` (see [IRED preparation](../../data/ired_preparation.md) and [Hydro preparation](../../data/hydro_preparation.md)). Use starting sets of 100 measured variants. The original starts are listed by seed in the manifests under `output/multiprotein/`; using fresh starts of your own is better.

## Outcome and hypotheses

The best measured score after the run, compared start by start, with differences of at most 10^-12 counted as ties. Expected if the earlier result holds: normal repair scores below fixed reward in a large share of starts; repair without the early stop is close to fixed reward and above normal repair. State your hypotheses before running.

## What not to do

Do not copy the predictor, the warning thresholds or the repair rules from this repository; the point is a separate implementation. Do not tune on the evaluation proteins. Report failures.

## Comparing

Compare your counts with the [findings](repair_without_stopping.md#findings). A match supports the finding; a difference is informative about what depends on implementation details.
