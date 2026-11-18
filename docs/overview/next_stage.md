<div align="center">

# Research for the next CERA stage

Planning note

</div>

Reviewed 16 November 2026 against the current [amylase range pilot](../studies/amylase/prediction_ranges.md#findings), existing code and primary sources below. This is research and planning, not an implementation decision, detector validation or final result. The pilot is one adaptive run on one dataset; its later-selected variants are not independent samples from an unchanged population.

## 1. What the current range result actually says

The pilot selected 100 new variants, all inside their saved ranges. Those ranges have constant width within a round, because the range-setting rule uses one error threshold for all candidates in that round. They are not scaled by model disagreement. A range's **coverage** is the fraction of later scores inside it; its **width** is the distance between its lower and upper limits. High coverage with a very wide range can be uninformative.

A post-hoc reconstruction from the saved pre-reveal records found mean absolute prediction error 0.051264 and mean range width 0.203374 across the 100 selected scores. The mean error describes the selected samples in this run; it is not the error on all candidates or future runs. All 66 selected original-train and all 34 selected original-test scores were inside their ranges; original split labels were attached only after selection. Per-round radii ranged from 0.095077 to 0.110822. The 20 range-setting cases are reused and future candidates depend on earlier decisions, so neither 100/100 nor the nominal 90% target establishes a coverage guarantee.

[Greenman et al. (2025)](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1012639) compared uncertainty methods on protein tasks using several metrics, including coverage and width, and found no method consistently best across settings. [Fannjiang et al. (2022)](https://pmc.ncbi.nlm.nih.gov/articles/PMC9618043/) analyze prediction under feedback-induced shift. Their specialized method has conditions and should not be assumed to apply unchanged to this pilot.

**Guidance:** repeat the current pilot under predeclared seeds, report per-run and per-batch coverage with counts and widths, and preserve each run's initial data and role assignments. Check the ranges on later scores saved before their revelation. Summaries across a few runs of one protein are descriptive and do not imply independent biological replication. Never adjust thresholds after seeing IRED or Hydro results.

## 2. Variable-width ranges are an option, not a free improvement

Our current symmetric range has the same width for every candidate in a round. A variable-width method could give different widths to candidates that appear more or less uncertain. For example, [conformalized quantile regression](https://proceedings.neurips.cc/paper_files/paper/2019/hash/5103c3584b063c431bd1268e9b5e76fb-Abstract.html) fits lower and upper predictions before a separate calibration step. Its theoretical results rely on assumptions that must not be transferred automatically to our adaptive search.

Another possible approach scales a range using the spread of the five models. That needs a precise formula, a rule for zero or tiny spreads, separation between model selection and range setting, and an independent comparison with the fixed-width pilot. A spread is the variation among the models; it is not a guarantee of the actual prediction error.

**Guidance:** keep the current range as a baseline. Investigate alternatives only with a predeclared amylase development comparison that reports both coverage and width, handles degenerate spreads, and retains the same measurement budget. Do not introduce a complex method merely to make ranges narrower.

## 3. A warning needs an independently defined event

The synopsis proposes checks for constraint violations, unfamiliar sequence representations, interval misses, model disagreement and low batch diversity. Some warnings are available before measurement; interval misses are only known afterward. An unfamiliar representation is a distance signal, not a demonstrated biological cause of error. A group of models can agree and still be wrong; uncertainty can degrade under shifted data. [Ovadia et al. (2019)](https://proceedings.neurips.cc/paper/2019/hash/8558cb408c1d76621371888657d2eb1d-Abstract.html) studied that issue in classification, so its results motivate caution rather than establish a protein-specific rate.

The current pilot has **zero interval misses**, so it cannot estimate how reliably a missed-range warning identifies actual misses in natural runs. A test that deliberately changes a predictor, range or constraint must first verify that the intended condition actually occurred; merely disabling a component does not prove a failure was injected. For each warning, define its timing, input, expected positive and negative examples, handling of too few points and ties, and the separate criterion used to judge it.

If true events are rare, a seemingly accurate warning can still generate mostly false alerts. **Precision** is the fraction of warnings that correspond to defined events; **recall** is the fraction of defined events that were warned about. If their denominators are zero, report the metric as undefined rather than inventing a value. [Saito and Rehmsmeier (2015)](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0118432) explain why precision and recall matter when positive examples are scarce; this concerns binary classification, so adaptation to each CERA warning still needs justification.

**Guidance:** begin with deterministic unit examples and a documented event ledger. Do not claim precision, recall, causal diagnosis or empirical warning rates from the current zero-miss pilot.

## 4. Distance thresholds need a reference that is not self-distance

The current ESM-2 representation turns a protein sequence into a vector of 320 numbers. Straight-line distance between two such vectors is a representation-space distance; it is not the number of amino-acid changes. For a known variant, the distance to a set that includes itself is zero. A threshold based on those self-distances would therefore be meaningless.

**Guidance:** if testing a nearest-known-distance warning, construct any reference distribution using each known point's nearest *other* known point, specify what happens when there are fewer than two points, duplicate or tied representations, and define the distance and threshold units. Evaluate the warning against separately defined future prediction misses; a large distance alone is not a demonstrated failure. The earlier amylase representation-distance analysis was post-hoc and cannot serve as a frozen threshold.

## 5. A replay check is not proof of repair

A replay asks what a changed ranking rule would have chosen among already-known cases. It can reject a proposed rule that violates constraints or repeats a previously observed mistake, but the repair was chosen using that same past evidence. Repeatedly selecting a repair because it looks good on those cases can fit the check itself. A later improvement must be judged on later pre-recorded predictions and newly revealed measurements, with matched comparisons.

This is related to the broader difficulty of estimating how a different decision policy would perform using data collected under the old one. [Su et al. (2019)](https://proceedings.mlr.press/v97/su19a.html) discuss the assumptions and bias issues in a different decision-making setting. CERA has a finite table of measured variants, which allows a separately run simulated policy to query its own choices; that does not make reusing a past replay for both selection and proof valid.

**Guidance:** first define the repair menu, costs, permitted inputs, verification checks, rollback and stopping. Then run a matched no-repair or fixed-penalty comparison with the same starting information and budget. Keep the synopsis's unresolved conflict between cheapest-valid and language-model-selected repairs visible; do not silently decide it by writing code.

## 6. Proposed order of work

1. Predeclare repeated-seed evaluation of the **existing** range pilot, including the random seeds, denominators, width and stop handling. Review every run, including failures. This is development on amylase, not a final claim.
2. Specify warning events and their timing, then test positive, negative and edge examples before running them against recorded or new experiments. Keep warning signals and inferred causes separate.
3. Compare any proposed variable-width range against the existing fixed-width range with matched amylase settings and no tuning on IRED or Hydro.
4. Define the rule-based repair and its checks, then evaluate later outcomes against matched non-repair baselines before adding the language model.

No additional implementation or pilot was run for this research review. The source-backed alternatives above are possible next investigations, not established improvements.
