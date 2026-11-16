# First amylase comparison: implementation plan

Status: planned, not implemented or approved for code changes. The purpose is to test the experiment machinery with two understandable methods, not to claim CERA's repair system works. This plan follows the [amylase development protocol](amylase_development_protocol.md) and the user's delegated research-design direction.

## What will be compared

Both methods begin with the same 100 revealed variants, the same eligible unmeasured pool, the same four-substitution development limit, and up to 100 additional measurements in batches of at most ten. They use separate run records and the same recorded initial-set seed. Record any difference in computation; do not treat the ten batches as independent experiments.

1. **Random selection:** choose eligible, unmeasured variants without using scores. A separately recorded random seed controls its selections.
2. **Greedy prediction:** use revealed sequence-score examples to predict the score of each eligible variant, then choose the highest predictions. Refit between batches using only permitted previously revealed examples. Break equal prediction ties using a stable candidate identifier.

A predictor is a mathematical rule learned from examples. For the first comparison, use ridge regression: a linear predictor that discourages overly large fitted weights. Represent each amino-acid position as indicator values identifying which letter occurs there. This is called one-hot encoding. Use the same fixed alphabet and positions for all variants; no score-derived feature selection. FLIP2 uses a comparable ridge/one-hot baseline, although its benchmark task is not identical to our sequential selection problem. [FLIP2](https://flip.protein.properties/); [ridge documentation](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Ridge.html).

Select the ridge penalty using cross-validation entirely within the fitting examples. Cross-validation repeatedly trains on one portion and checks another. Any learned preprocessing must be fitted inside each training portion. This development-stage score-based tuning is not an unbiased final performance estimate. [Scikit-learn guidance](https://scikit-learn.org/stable/common_pitfalls.html#data-leakage).

For compatibility with the provisional protocol, split the initial 100 into 80 fitting and 20 reserved examples without using scores; record the assignment and seed. Newly revealed measurements are available for fitting after their predictions and scores have been recorded. The initial 20 remain reserved. This comparison does not calculate prediction intervals, so it must not claim coverage or treat the 20 reserved examples as independently validated calibration. Random selection can ignore the fitting/reserved distinction but has access to the same initial measurements.

## Required runner changes

- Expose the sequences associated with already-revealed identifiers through a supported interface; `revealed` currently provides scores only and `candidates` excludes known sequences. Do not expose hidden scores or original split metadata.
- Record greedy predictions and the selected identifiers before revealing scores. A failed write must stop the operation. Random selection has no model prediction; its recorded seed and selected identifiers must be sufficient to audit the choice. Include method, settings, version information, seed, and role assignment in the saved record.
- Match the starting examples across methods and validate this from the saved records. A score or identifier must not be queried twice in the same run.

## Outputs and checks

- Save each run's selection and reveal events, plus a small per-batch table of actual new-measurement count and best score observed so far, including the starting set. Record an early stop rather than inventing later observations. Produce a simple plot only if it can be generated without obscuring the underlying table.
- Use invented small datasets to check that known sequences and scores match, hidden scores remain unavailable through the supported interface, predictions precede revelation, tie-breaking and random selection are repeatable, and the methods have identical initial examples, candidate eligibility and budgets.
- Independently reconstruct the best-so-far table from saved records and verify partial batches, budget accounting and stop reasons. Check that the existing runner and catalog still pass their checks.
- Run a small amylase development comparison only after the checks pass. Record the exact commands, dependency versions, parameters, random seeds and output files. Any result is exploratory and cannot demonstrate repair or broad biological generalization. Do not tune using IRED or Hydro.

## Dependency and scope

The current system Python has NumPy 2.4.6, SciPy 1.18.1 and scikit-learn 1.9.0 installed, but these are not declared in the backend requirements. Before implementing, verify the installed APIs and choose an explicit, reproducible dependency specification appropriate for the project; do not assume another environment has these packages. Keep dataset loading, runner, selection methods and result reporting in focused modules, consistent with Varun's backend organization request. Preserve the current web catalog API.

Not in scope: ESM-2, predictor ensembles, intervals, failure detectors, repairs, language models, full benchmark evaluation, or a claim that either simple method is optimal. The existing runner's file/object access boundary is not a security sandbox; incomplete logs after interruption require inspection.
