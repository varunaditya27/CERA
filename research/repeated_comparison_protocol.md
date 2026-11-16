# Repeated amylase development comparison

Recorded before the repeated runs on 16 November 2026. This is exploratory development on amylase, not the final CERA evaluation. The existing [first comparison plan](first_comparison_plan.md) and [amylase development protocol](amylase_development_protocol.md) still apply.

## Motivation

In the first exploratory run, random selection queried 49 original-train and 51 original-test variants; the greedy predictor queried 100 original-train and zero original-test variants. These counts were calculated after the run from its identifiers and the source file. They show where each method searched; they do not establish why it chose those variants. Do not feed the original split labels or unqueried scores back into selection.

## Predeclared runs

- Run ten matched pairs with initial-set seeds 2 through 11 inclusive. Both methods within each pair receive the same initial set, source data, candidate constraints and maximum budget.
- Use selection seed 1000 plus the initial seed, and data-role seed 2000 plus the initial seed; the predictor's cross-validation seed equals the initial-set seed. These are recorded in each run. Do not choose seeds after seeing results.
- Use the existing implementation without changing method settings in response to these runs. Each pair retains complete selection, prediction and measurement records and score tables. The earlier seed-1 run is separate because its selection and role seeds differ.
- Check each pair's matching initial data and settings, selection/reveal order, unique queries, budget accounting, summary reconstruction and greedy ranking. Report failures and incomplete runs rather than excluding them silently.
- Report all per-pair final best scores and differences, plus original split counts of newly selected variants. Record the number of pairs where each method's final best score is greater or tied. Do not call the runs independent biological datasets or treat ten batches in a run as ten repetitions. Do not infer broad significance or a general biological winner from ten runs on one dataset. [Paired comparisons](https://www.itl.nist.gov/div898/handbook/prc/section3/prc311.htm); [randomness and reproducibility in model comparisons](https://proceedings.mlr.press/v97/bouthillier19a.html).

The current runner keeps selection and role seeds fixed by default when called through its command-line script; these runs explicitly supply the seeds through its existing Python interface. Nothing here claims calibration, failure detection or repair has been implemented.
