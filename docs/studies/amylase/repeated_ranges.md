<div align="center">

# Repeated amylase prediction-range development runs

Protocol and findings

</div>

## Protocol

Recorded before running on 16 November 2026. These are exploratory checks of the existing fixed-width prediction-range pilot, not a final evaluation or proof of coverage. The [range development plan](prediction_ranges.md#plan) and [next-stage research](../../overview/next_stage.md) apply.

### Predeclared procedure

- Run ten additional pilots using initial-set seeds 2–11. For each seed `s`, set the role-assignment seed to `2000 + s` and the member-seed generator seed to `3000 + s`. These choices are made before observing results. The earlier seed-1 pilot is separate because its role and member seeds differ.
- Keep the same pinned amylase representations, four-substitution eligibility limit, 100 starting measurements, 20 reserved range-setting examples, five ridge predictors, nominal 90% target, batches of up to ten and maximum 100 new measurements. Do not tune the model, threshold, seed choices or budget based on these results.
- Preserve each complete run's full pre-reveal predictions, ranges, method settings, fitting identifiers, scores and stops. Compress the completed JSONL record losslessly with gzip, keeping the per-run CSV table. Record a fingerprint of the uncompressed record and compressed file so reviewers can verify them; no measurements or predictions are discarded.
- Attempt and report every declared seed. A failed or stopped run is recorded with its actual stop or error, rather than omitted or padded with invented observations. Do not adjust the denominator to 100 if fewer scores were revealed.
- Independently audit initial and reserved sets, seed settings, model-fitting membership, pre-reveal ordering and candidate ranking, unique queries, original data scores, range bounds, remaining-budget arithmetic, and coverage/width reconstruction. Match the cache and code fingerprints to the actual files. Count original split labels only after selection; do not feed them back to the selector.
- Report each run's covered count and denominator, coverage, mean width, selected original split counts and stop. Summarize the distribution of per-run coverages and widths, but do not treat 100 measurements within a run or ten runs on one protein as independent biological datasets. The 90% value is a nominal target, not a guarantee under adaptive selection and reused range-setting data.

The intention is to understand variability in this one development dataset, not to compare selection policies, infer repair effectiveness, establish causal effects or tune against IRED or Hydro. The research reasons for reporting width together with coverage are in [Greenman et al. (2025)](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1012639), and the feedback-dependence limitation is discussed by [Fannjiang et al. (2022)](https://pmc.ncbi.nlm.nih.gov/articles/PMC9618043/).

## Findings

Completed 16 November 2026 under the [predeclared protocol](repeated_ranges.md#protocol). This is exploratory work on amylase, not a final evaluation, proof of 90% coverage or a CERA repair experiment.

### Results

All ten declared runs completed ten batches and spent their maximum 100 new measurements. Per-run observed coverage ranged from **76/100 to 100/100**; per-run mean interval width ranged from approximately **0.1321 to 0.1999** score units. Across the ten runs, 899 of 1,000 selected scores were inside their saved pre-reveal intervals, and the average of the ten mean widths was approximately 0.1760. The pooled 89.9% happens to be close to the nominal 90% target, but does not establish a coverage guarantee or erase the substantial differences between runs.

These ten runs share one underlying protein dataset; selected examples and successive rounds are dependent. The fraction is a descriptive result for these simulated searches, not a confidence interval, ten independent biological replications or a claim about unselected variants. Standard conformal guarantees cannot be assumed under adaptive selection and repeated use of the reserved range-setting examples. [Fannjiang et al.](https://pmc.ncbi.nlm.nih.gov/articles/PMC9618043/) analyze the complications of feedback-dependent biomolecular design.

See [summary.csv](../../../output/amylase/search/amylase_ranges_repeated/summary.csv) for each seed's covered count, denominator, coverage, width, original-split counts and stop. The earlier seed-1 pilot is separate; its role and member seeds were different. All split labels in the summary were joined after selection.

### Independent checks

For every run, checked the starting set, 20 reserved examples, predeclared seeds and member seeds, fitting/reserved separation, source and cache fingerprints, score-reveal order, ranking of selected candidates, unique selections, source measurements, interval bounds, budget arithmetic, stop state and reconstruction of the coverage CSV. All 100 batches passed.

As a second calculation, reconstructed all 100 five-model groups from their saved fitting identifiers, measurements and member seeds. For every batch, independently re-ran cross-validation to check the chosen penalty, recomputed the 19th of 20 reserved errors, and reproduced the selected candidates' recorded mean predictions and model spreads within `1e-12` in the current environment. This uses the same underlying scikit-learn algorithms and is a reproduction check, not independent scientific validation.

Complete records are stored losslessly as `seed_02/run.jsonl.gz` through `seed_11/run.jsonl.gz`; [record_fingerprints.csv](../../../output/amylase/search/amylase_ranges_repeated/record_fingerprints.csv) records the compressed and original uncompressed SHA-256 fingerprints. Each seed directory retains its coverage CSV. The files can be read with standard gzip tools without altering their contents.

### Post-hoc warning-threshold inspection

After the runs, inspected the synopsis's proposed rule: observed coverage below 0.75 over the latest 30 revealed measurements, evaluated at batch boundaries after at least three batches. Seven of the 80 overlapping three-batch windows met that rule, across seeds 4, 6, 8 and 9. This inspection was not part of the predeclared summary; windows overlap and are not independent, and no warning detector was implemented. It is an example of where the proposed rule would have fired, not a precision, recall or false-alarm estimate and not evidence about the cause of low coverage.

### Next investigation

The data now contain both covered and missed selected scores, unlike the first pilot. Specify warning rules and their timing, independently defined events and edge cases before implementing detectors. Keep the current fixed-width ranges as a baseline and investigate whether changes improve coverage *and* informativeness without using IRED or Hydro to tune. Repairs remain unimplemented; a warning alone does not prove its cause or that a proposed repair works.
