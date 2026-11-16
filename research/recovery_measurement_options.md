# Options for measuring recovery of prediction ranges

This is a proposal for review, not an implemented or frozen research metric. It addresses one kind of warning: measured scores missing their previously recorded prediction ranges. It does not define recovery from low diversity, model disagreement or constraint violations.

## The problem in plain language

Imagine a range is a forecast that a variant's measured score will fall between two values. Coverage is the fraction of actual scores that land inside their forecasts. CERA's target is 90%, but its choices deliberately focus on promising variants, so 90% is a target to observe, not a guarantee. Range width must be reported alongside coverage: a very wide range can cover many outcomes while saying little.

A failure warning currently uses the latest 30 measured variants and triggers below 75% coverage. A later return to acceptable coverage would be an observed recovery, not proof that a repair caused it. Search choices, model refitting and chance also affect the result. Different warning and recovery thresholds create a gap: 75% to 85% is neither a new failure warning nor the proposed recovery band.

## Three options

1. **One later batch of ten.** Call it recovered when 9 of the 10 later scores fall inside their saved ranges, as in the original synopsis. This is easy to explain and detects changes quickly, but one score changes coverage by ten percentage points. Exactly 8/10 or 10/10 misses the synopsis's 85–95% band, even though 10/10 is not evidence of insufficient coverage. It is useful as a descriptive batch measure and weak as a standalone recovery claim.
2. **Thirty new measurements (recommended development definition).** At the first coverage warning, start counting *subsequent* measurements, excluding all 30 that produced the warning. At the end of each later batch, examine the latest 30 subsequent measurements; call the first such window with observed coverage from 85% to 95% inclusive a recovered window. For exactly 30 values, that means 26, 27 or 28 inside their saved ranges. Record the number of subsequent measurements needed, the coverage and mean width. This reduces single-batch granularity and uses entirely later observations, but still provides noisy evidence on adaptively selected examples and has only up to 100 new measurements in total. Sliding windows overlap, so repeated eligible windows are dependent. A result above 95% should be reported separately as high coverage rather than described as undercoverage; it can also signal overly broad ranges.
3. **All later measurements combined.** After a first warning, summarize coverage and width across everything remaining, without claiming a recovery time. This uses the most available later observations, but results combine different stages and can mask both early recovery and later decline. Early stops leave less evidence.

For options 1 and 2, count only the first warning and first qualifying later window per run in the primary summary. Report the number of warned runs, recovered runs, runs that stopped before recovery and runs that exhausted their budget without recovery. Distinguish no warning from too little subsequent data, and distinguish a repair-related stop from budget exhaustion. Never assign a recovery time to a run that did not recover. The number of additional measurements, not calendar time, is the primary elapsed measure.

## Worked examples from saved development runs

- Seed 31, targeted repair: the first four batches covered 6/10, 8/10, 4/10 and 8/10. The existing 30-measurement warning triggers after the third batch (18/30). Only ten later measurements are available before a failed-repair stop. Option 2 cannot determine a 30-measurement recovery window; it must report insufficient follow-up and the stop reason.
- Seed 34, targeted repair: the first seven batches covered 9/10, 6/10, 9/10, 8/10, 9/10, 10/10 and 10/10. Its saved coverage warning did not trigger. It therefore has no coverage-warning recovery episode, even though it stopped for failed repairs involving other warning types.

These examples were selected after inspecting the development records and are illustrations, not an independent evaluation or evidence of causation.

## Important interpretation

The observations in a search are adaptively chosen and share models and training examples; ordinary independent-binomial confidence intervals should not be asserted without checking assumptions. A stop can prevent future recovery from being observed. It is not automatically equivalent to ordinary random loss to follow-up; time-to-event analyses distinguish such competing outcomes from censoring, as explained in this [primary competing-risk methods paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC8986229/). For this small study, report counts and individual trajectories rather than fitting a survival model by default. If a later protocol uses a more formal model, state its assumptions and estimand first.

Comparing recovery only among runs with a warning can be misleading: different methods may trigger warnings for different reasons or at different times. Report all runs' warning and stopping rates alongside any conditional recovery summaries, and do not interpret a post-warning association as a causal effect of a repair.
