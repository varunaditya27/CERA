<div align="center">

# Research guidance for implementing CERA

Background

</div>

Reviewed 16 November 2026. This record connects primary research and official documentation to the current repository. A research finding is not proof that a proposed CERA component will work. Development decisions remain provisional until checked on amylase; IRED and Hydro should not be used to tune the method.

## 1. Start with the actual measurement

A protein sequence is a chain of amino acids. An assay is a laboratory procedure that measures a property of a sequence variant. The data give us previously measured variants and scores; CERA simulates selecting which already-recorded score to reveal next. It cannot establish that a newly designed, unmeasured protein will work. In the current catalog, amylase describes stain removal, IRED describes enzyme screening, and Hydro combines variants from three proteins. Confirm source details and score direction separately for each; see the [dataset ledger](dataset_evidence_ledger.md).

**Source:** [FLIP2 benchmark](https://flip.protein.properties/) describes the proteins and split rules. Its repository provides measured benchmark data, not evidence that CERA's proposed repair method works.

**Implication:** Record source version, score meaning, reference, eligible set and target direction for each experiment. The present runner is amylase-specific. Its data boundary prevents accidental access through its supported interface; raw files and Python internals are not a security boundary.

## 2. An accurate predictor and a useful search are different goals

The predictor estimates scores; the search decides which variants to query. In FLIP2, ridge regression on simple sequence indicators was often competitive with more complex predictors, although results varied across tasks and the benchmark's prediction tests are not the same as CERA's sequential search. [FLIP2](https://flip.protein.properties/).

In our ten exploratory amylase pairs, greedy selection found a higher final score in nine, but chose no original-test variants. A higher median prediction for the shifted group coexisted with training-side candidates occupying the very top ranks. The analysis is post-hoc, and the model's zero coefficients for unobserved sequence indicators do not by themselves prove why selection stayed on one side. See [our findings](../studies/amylase/repeated_comparison.md#findings).

The 2025 protein uncertainty benchmark by [Greenman, Amini and Yang](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1012639) found no uncertainty method best across all datasets, splits and metrics; their uncertainty-based optimization approaches often did not outperform greedy selection. Their study is evidence for testing simple comparators, not proof the same ranking will occur for CERA.

**Implication:** Keep random and greedy comparisons; report score trajectories and where candidates were selected from after the run. Do not force a shifted-side-only search while presenting it as the approved broad-pool experiment. A separately defined shifted-side experiment could be studied later, with Hydro's label-derived split issue addressed explicitly. Use controlled experiments to evaluate whether representation, candidate restriction, or a selection rule causes an observed behavior; do not infer cause from one correlation.

## 3. Uncertainty and prediction ranges need independent checks

An ensemble is a group of models whose predictions can differ. Disagreement is a warning signal, not a guarantee that the models are correctly uncertain or that the cause of an error is known. A prediction interval is a range intended to contain a later measured score. Coverage is the fraction of later measurements inside their previously recorded ranges; width tells us how informative those ranges are.

Ordinary split-conformal prediction uses examples reserved from model fitting to set the range. Its standard interpretation depends on assumptions about how the reserved examples and future examples relate. CERA deliberately chooses future candidates based on previous results, so it cannot simply promise 90% coverage. [Fannjiang et al. (2022)](https://pmc.ncbi.nlm.nih.gov/articles/PMC9618043/) study feedback-induced shift and a specialized method with its own assumptions; adopting their method is not automatic. The [Greenman et al. benchmark](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1012639) also measures coverage and width alongside other properties.

**Implication:** Start with the documented 80 fitting / 20 range-setting initial allocation only as a development choice. Save intervals before revealing each score, report coverage and width with the number of observations, and compare against later revealed measurements rather than reusing the range-setting data as independent evidence. Analyze repeated reuse of the same range-setting examples and adaptive feedback before claiming any theoretical guarantee. A target is not an achieved result.

## 4. A warning is not necessarily a diagnosed cause

The synopsis proposes warnings for constraint problems, unfamiliar candidates, interval misses, model disagreement and lack of batch diversity. Some use revealed measurements; others can be observed before measurements. A warning that an unusual variant was also predicted poorly is useful evidence, but does not prove unfamiliarity caused the mistake.

[Neural network extrapolation to distant regions of the protein fitness landscape](https://www.nature.com/articles/s41467-024-50712-3) reports that different model architectures can infer different landscapes from the same data. This is consistent with checking multiple models but does not make disagreement a ground-truth label for failure. The article's full text was unavailable through the browsing tool during this review; this point relies on the abstract and should be revisited against the full paper before a detailed implementation claim.

**Implication:** For each warning, specify what evidence it reads, when it fires, how it is tested, and where it can be wrong. Establish independently defined positive and negative examples before reporting detector precision or recall. Keep score prediction, warning detection and claims about causes separate.

## 5. Repairs need to affect something the checks can observe

The proposed system changes a scoring rule after a warning. A rule change that adjusts only the ranking of candidates may leave the predictor's numerical outputs and prediction ranges unchanged. Consequently, unchanged prediction correlation or interval coverage cannot by itself establish the ranking change worked. Conversely, passing a replay on already-seen cases does not prove a future benefit.

**Implication:** Validate allowed fields, ranges and constraints before accepting a repair; record the previous version, proposed change, evidence and outcome; keep or restore the previous valid rule on failure. Measure subsequent effects on later scores, alongside fixed-penalty and retraining comparisons given matching starting examples, candidate access and budgets. The synopsis's cheapest-valid repair and language-model-selected repair rules still need a precise resolution. Do not call a checked repair scientifically successful until future evidence supports it.

## 6. ESM-2 implementation is a separate, testable stage

ESM-2 is a pretrained protein-sequence model. An embedding is the numerical representation produced for a sequence; it is not itself a measured fitness score. The synopsis proposes the small [ESM-2 8M checkpoint](https://huggingface.co/facebook/esm2_t6_8M_UR50D). The original [ESM repository](https://github.com/facebookresearch/esm) is archived, while [Transformers' ESM documentation](https://huggingface.co/docs/transformers/model_doc/esm) describes a supported model interface. The original repository's sequence-representation example averages residue positions while excluding boundary tokens. The exact model files, library versions, tokenization, handling of padding and boundary tokens, pooling, precision and dataset-to-cache mapping must be recorded and tested.

On this machine on 16 November, package metadata reported PyTorch 2.14.0, Transformers 5.16.1, and no installed `fair-esm`; `nvidia-smi` reported an RTX 5050 Laptop GPU with 8,151 MiB total and 7,758 MiB free at that instant. These observations do not verify that the checkpoint loads, that the GPU is usable by PyTorch, or that a particular batch size fits. Free memory is temporary.

**Implication:** Before a full dataset run, verify the exact installed APIs and checkpoint revision; run short and full-length representative sequences; compare a sequence embedded alone and in a padded batch; check output dimensions, finite values and deterministic behavior; measure elapsed time and peak memory; and make cache identity include the source fingerprint, sequence identity, checkpoint and representation settings. The checkpoint or alternative interfaces have not yet been benchmarked in this project.

## 7. Research-grade records and fair comparisons

The [scikit-learn leakage guidance](https://scikit-learn.org/stable/common_pitfalls.html#data-leakage) explains that transformations learned from evaluation data can contaminate model selection. CERA additionally needs to prevent hidden measured scores and score-derived split labels from reaching a selector. In Hydro, membership in a score-defined split can itself reveal information about an unseen score.

**Implication:** Use same starting measurements, eligible candidates, budget and stopping definitions for matched methods. Keep data-dependent preprocessing inside fitting folds, record model settings and predictions before reveal, and calculate full-pool metrics only in a separate retrospective evaluation. Preserve all failed and stopped runs. Ten repeated seeds on one protein dataset quantify some run-to-run variability but are not ten independent biological datasets. The current run records and repeated amylase summaries are exploratory; they cannot establish broad statistical generalization.

## 8. Recommended immediate sequence

1. Specify a controlled amylase analysis to test competing explanations for the observed rankings using recorded predictions and permitted data; define what each outcome would mean before running it. Retain the approved broad-pool protocol.
2. Before writing embedding code, inspect installed API behavior and prepare representative model-loading, pooling, caching and hardware checks. Pin exact versions and checkpoint revision after validating compatibility.
3. Add an ensemble and prediction ranges only after the representation and data-role rules are testable. Evaluate pre-reveal coverage and width empirically; do not infer guaranteed coverage under adaptive search.
4. Define each warning and repair with positive, negative and edge-case checks; implement and compare a rule-based repair before assessing whether a language model contributes.

These are recommendations and implementation gates, not evidence of completed experiments. IRED filtering (later largely explained; see [IRED preparation](../data/ired_preparation.md)), Hydro construct provenance (the reference mappings and scores were later matched to the source table; see [Hydro preparation](../data/hydro_preparation.md)), recovery definitions, and the language-model repair-order conflict remain open. No new application code or model was run for this research review.
