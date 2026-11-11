# CERA Research Evidence and Project Roadmap

Working proposal for Varun Aditya and Ravi | Evidence reviewed 9 November 2026

## Purpose and reading guide

This document is the working reference for understanding CERA, agreeing on the experiment, and dividing the remaining work. It distinguishes established facts, direct checks of the local files, proposals that still need agreement, and open questions. It does not claim that CERA has produced experimental results. Where this proposal changes or clarifies the submitted synopsis, the team should record its decision and seek the project guide's agreement when required.

The central research question is: when a protein search is misled by an inaccurate learned score, does a detected warning followed by a constrained, checked change to that score improve subsequent search outcomes compared with fair simpler alternatives? The answer may be yes, no, or dependent on the dataset. Report all of those possibilities honestly.

## 1 From protein to project

A protein is a chain of amino acids, written as letters. A variant is a related sequence with one or more substitutions. For example, changing an A to a V at one position creates one substitution. A reference or wild type is the sequence used as the starting point for counting such changes; the exact reference must be verified for each dataset. A laboratory assay is a procedure that measures a property, such as stain removal or fluorescence. The resulting numerical measurement is called the target, label, score, or fitness in different sources. In this document, measurement means the recorded experimental score, and fitness refers to the property being optimized; we must establish whether a larger measurement is better for each assay.

The ordinary laboratory process is sequence -> experiment -> measurement. In CERA the measurements already exist in public data. We simulate sequential experiments: a search sees candidate sequences, asks for a limited number of measurements, and uses those revealed measurements to choose later candidates. This is a retrospective, finite-pool study: it chooses among measured variants already present in a file. It is not a new laboratory experiment and does not establish that an unseen designed protein will work.

A prediction model learns a relationship between sequences and revealed measurements. Its predicted fitness can be wrong. A search that repeatedly follows high predictions may find variants whose apparent value reflects model error. A reward is the numerical rule that combines a predicted score with other terms to rank candidates. CERA proposes to detect warning patterns, select a permitted change to this rule, check it, and compare future outcomes with methods that do not use the same repair strategy. The synopsis describes this as specify, search, falsify and repair. [1, 2]

A counterexample is evidence that a claim or expectation failed. Some proposed CERA events are observed prediction failures after measurements; others, such as low batch diversity or disagreement among models, are warnings available before measuring. Calling both recorded warnings avoids implying that all five are proven label contradictions or proven root causes.

## 2 One run from beginning to end

Imagine Ravi evaluates alpha amylase. The team has first agreed which sequences are eligible, which initial measurements may be used, and the maximum number of additional measurements. The initial predictor is fitted using only permitted revealed values. Candidate sequences are visible; their hidden measurements and label-derived summaries are not sent to the selector.

For each round the system records the model version, predictions, prediction intervals, which candidates are allowed, current reward and planned batch before opening any new measurements. It reveals only the chosen batch, logs the count, compares actual outcomes with the saved predictions, and records any warnings. A repair changes an allowed parameter or rule. A verifier checks validity and specified evidence; acceptance means the repair passed those checks, not that future improvement is guaranteed. The system either continues with the new rule, retains the previous rule, or stops under a predefined condition. A separate evaluator computes results after the run using information unavailable to the search.

A large language model, or LLM, is a text-processing model. The proposed LLM may translate a goal into a restricted specification and suggest a permitted repair. Ordinary code checks its output, scores candidates, applies constraints, counts measurements, and records events. The LLM must not receive hidden measurements or write and execute arbitrary reward code. A rule-based version is needed to test whether the LLM adds anything. Provider, model, cost, access and whether responses can be reproduced are not established. [1, 2]

## 3 What exists and what does not

Verified in the repository: raw files for five datasets; download and structural-audit scripts; source and usability notes; a read-only web catalog with health and dataset endpoints; an interface with overview, datasets, dataset profiles and method pages; and the synopsis and briefing. The data audit and file verification completed successfully on 9 November 2026. A frontend production build passed in the current execution environment. Earlier build failures occurred in a restricted environment; the exact cause was not established.

Not implemented in the inspected application: experiment runner; measurement-hiding interface; fitting or embeddings; sequential candidate selection; budget enforcement; failure detectors; repairs and verification; LLM integration; comparison experiments; results. The backend catalog does not expose scores through its endpoints, but anyone or any program with file access can read the raw CSV scores. A future experiment must enforce its own information boundary. Existing checks validate file structure, not the scientific conclusions of this proposal. [3, 4]

## 4 Evidence for the datasets

The local audit found unique sequences, standard amino-acid letters, finite numerical measurements, expected columns and row counts. It also checked that the four local FLIP/FLIP2 CSVs match their gzip archives. These checks do not establish that all source metadata, score directions, or licenses are correct. FLIP2 publishes benchmark rules for position, mutation-count, fitness and reference-protein shifts. [3, 4, 5]

### Alpha amylase

The close-to-far file contains 3,706 variants: 1,782 marked train and 1,924 test. The original authors' 425-residue reference sequence matches the local sequence length. A direct local comparison against the original authors' combinatorial data matches all 3,706 sequence/target pairs to stain_activity within 1e-8. The original paper describes stain removal activity, so higher values mean greater measured stain-removal activity. Record the source and units in the dataset record before formal runs. The benchmark calls the split a position shift: train mutations near the active site and test mutations farther away. [5, 6, 7]

With the source reference and a maximum of four substitutions, a local count found 1,566 train and 1,709 test variants eligible. The reference sequence itself occurs once on the test side. A team must therefore specify whether a reference sequence is initially measured, eligible to be queried, or excluded; it cannot assume the split always puts it in training. The four-substitution count is a candidate policy calculation, not an instruction to adopt this limit.

### Imine reductase

The local two-to-many file contains 8,586 variants: 4,408 train and 4,178 test. The benchmark describes training on variants with at most two substitutions and testing on variants with more. An independent match of all local sequence and target pairs to the original lab's active-data file, after removal of terminal stop markers from source sequences, identifies the corresponding 290-residue reference from the source WT field. Under a maximum of four substitutions, 4,408 train and 3,225 test variants are eligible; the latter comprise 2,053 with three substitutions and 1,172 with four. The original lab archive describes fitness as a logarithm of enrichment compared with the original enzyme: a higher value means the variant became more common after selection, relative to its starting amount. Record the exact assay version and treatment of inactive variants before a formal experiment. [5, 8, 15]

The benchmark website lists 17,143 variants, whereas the local split contains 8,586. The original active-data file contains 10,905 rows and the source describes a broader screened collection including inactive variants. The original file has 2,319 records without a local match; 12 of these retain a standard 290-residue sequence after removal of a terminal stop marker, while the others contain internal or nonstandard symbols and/or different lengths. This is consistent with a filtering contribution but does not establish the precise inclusion procedure or explain all 12 cases. Preserve the discrepancy and do not state that the filtering chain is resolved.

### Hydrophobic core

The low-to-high file contains 24,935 variants of three proteins with sequence lengths 57, 63 and 65. Local split counts by length are respectively 5,390 train / 4,582 test; 4,867 / 1,596; and 2,210 / 6,290. Independent alignment to UniProt sequences gives a strongly supported mapping: length 57 to P06241 residues 85–141; length 63 to P01053 residues 22–84; length 65 to P0A9X9 residues 5–69. Across each group all local differences from the corresponding segment occur at seven construct positions. These are sequence-derived reference mappings, not yet confirmation of the exact experimental construct provenance. [16] The benchmark describes the low-to-high split as below versus above median fitness. The unequal counts mean it should not be described as a separate median-based split for each protein without checking the original preparation. [5]

Relative to the inferred reference segments, a four-substitution cap leaves 263 train / 747 test at length 57; 713 / 579 at length 63; and 701 / 2,215 at length 65. These counts depend on the inferred references. The smallest train group has only 263 candidates before validation and other exclusions, so check whether 100 initial examples remain feasible. Recommendation for agreement: run and report a separate search for each verified protein, preserve the original split labels, and compute within-protein comparisons. Do not count residue differences between unequal-length proteins as a simple substitution count or mix their raw measurement scales without a justified transformation. A score-defined split also provides label-derived information when it is used to choose initial examples. This privileged retrospective assumption must be disclosed.

### GB1 and GFP

GB1 has 8,733 variants (5,089 train / 3,644 test). The original FLIP documentation identifies four variable sites and states that its low-vs-high split assigns below-wild-type fitness to training and the remainder to testing. It says the full reference sequence was inferred; the local validation field also contains blanks whose handling should be established before use. Source notices concerning modified-data licensing should be reconciled before redistribution. GB1 is an optional additional benchmark, not a substitute for the primary evaluation unless the plan is formally revised. [9]

GFP contains 51,714 variants. Its ProteinGym columns differ from FLIP's and no existing train/test split is provided in this local assay file. ProteinGym's own documentation says higher final DMS_score corresponds to higher fitness. The current local audit reports 35,584 variants within four substitutions of its supplied reference; verify the reference and mutation parser again when implementing the adapter. Define a label-safe initial split and confirm the original assay's redistribution terms before using it as an optional extra. [4, 10]

### Source and licensing boundary

FLIP2 lists MIT for amylase and CC BY 4.0 for IRED and Hydro. Retain the actual notices and required attribution in any redistribution. The original GB1 documentation and archive notices differ in their descriptions of modified-data licensing, and ProteinGym's software license alone does not establish the terms of every assay file. These are unresolved source-review items, not a legal conclusion. The files have already been committed locally; no external publication or distribution is assumed. [3, 5, 9, 10]

## 5 The experiment rules to agree before coding

### Candidate pool, starting data and split

The synopsis proposes making all eligible measured sequences available as candidates and drawing initial labels from the train side. If that is adopted, the benchmark split describes the initial information and intended shift; it does not guarantee the search subsequently chooses the test side. Report selection counts from each original side after the run. A shifted-side-only candidate setting may be a useful separate experiment, but it is a different experiment. Hide score-derived split membership from the selector where that membership would disclose hidden label ordering. The constructor's use of fitness-based split membership to choose starting data is still privileged retrospective information and must be disclosed.

### Budget and randomness

The synopsis proposes 100 initially revealed measurements plus up to 10 batches of 10 additional measurements, repeated for 10 random seeds. This is 100 initial plus at most 100 new, or at most 200 known by the end; it is not a total budget of 100. A random seed is a recorded value controlling randomized choices. Ten runs are a proposal, not proof of statistical precision. Verify sufficient eligible candidates and calibration samples for every dataset and constraint before freezing the configuration.

All methods must receive the same initial examples, accessible candidate pool, mutation constraints, maximum new-measurement budget, and definitions of cost. Differences in model, retraining, scoring, and stopping must be intentional and reported. An early-stopped method may spend less than its maximum; plot results against actual measurements and show stop rates rather than inventing later results. Define how partially filled final batches and empty pools behave.

### Data roles and leakage

Information leakage is use of an answer or answer-derived statistic before the experiment rules permit it. Keep fit data, calibration data, revealed audit data and final evaluation roles explicit. A validation column from an existing benchmark is not automatically the correct calibration set for this new experiment. Record the selection, prediction and interval before revealing the next batch. Do not use hidden scores, full-pool score statistics, a global best score, or score-derived partition metadata in selection or tuning. The final evaluator may use full scores for measures agreed in advance after a run, without feeding them back into search.

Using the calibration examples to select a prediction interval and then checking that same interval on those examples is not independent verification. Repeatedly selecting repairs against the same revealed cases may also overfit. A replay is a guardrail that checks known evidence; evaluate future effects using later predictions recorded before those measurements are revealed.

### Development, evaluation and limited claims

Use alpha amylase for development and tune decisions there. Freeze the experiment rules before the primary IRED and Hydro runs and record any later changes. A queried test-side variant is no longer an untouched test label for that run; evaluate the sequential search rather than describing adaptively queried values as a permanently held-out test set. Reporting on a few protein groups and ten repetitions does not establish broad biological generalization.

## 6 Prediction, uncertainty and candidate scoring

The submitted plan proposes frozen ESM-2 8M embeddings, a group of 5 to 10 models that predict numerical scores, and prediction intervals with a 90% target. An embedding is a numerical representation of a sequence; frozen means its model weights are not updated during this project. The original ESM repository lists the 8M model with 320 features, and its mean-pooling example excludes special sequence-boundary tokens. Record the exact checkpoint, tokenization, pooling, sequence order, cache version and checksums. The repository is archived; do not assume future software compatibility. [11]

An ensemble combines multiple predictors. Variation between their outputs is a useful diagnostic, but it is not automatically a complete or calibrated estimate of uncertainty. A prediction interval is a range intended to contain a future score. Coverage is the fraction of scores falling inside their previously recorded intervals; width measures how broad the ranges are. Standard split-conformal intervals require a separate calibration set and assumptions about how calibration and future examples relate. Adaptive selection deliberately changes the next examples, so ordinary 90% coverage is an empirical target here, not a guarantee. Report width along with coverage; an excessively wide interval can cover more outcomes without being informative. [12, 13]

The synopsis's reward combines predicted fitness, penalties for uncertainty and distance, constraint handling and a diversity term. Before implementation, define each quantity and scale, admissible parameter ranges, tie-breaking, and whether a term is a hard filter or a soft preference. Hard mutation rules should be enforced before selection; deliberately disabling a filter belongs only in a controlled detector test.

A crucial definition: if a known sequence's distance to the nearest known sequence includes itself, every such distance is zero. The reference distribution for a distance limit for the support warning must exclude self-matches, for example with nearest-other-known distances, and specify behavior for fewer than two known points or tied representations. Distance in embedding space and the number of substitutions from a reference are different quantities with different units. The synopsis defines a trust radius using the former but illustrates it with a change in mutation count; do not treat them as interchangeable.

The machine inspected has an NVIDIA GeForce RTX 5050 Laptop GPU reporting 8,151 MiB and approximately 22 GiB system RAM. A minimal GPU tensor operation succeeded. This does not establish that the full model, chosen batch size or end-to-end pipeline will run efficiently or fit in memory. Benchmark representative long and short sequences and record timing and peak memory before committing to a processing plan.

## 7 Auditing and repairs

The synopsis lists five warning types: constraint violation, support shift, miscalibration, model disagreement and diversity collapse. Their triggers are initial proposals, not established diagnostic tests. Support shift can indicate that unusual candidates and prediction misses occur together; it does not prove why predictions failed. Model disagreement and batch similarity may be visible before labels. Record warning type, trigger, stage, thresholds, inputs, and evidence; when several fire, define priority and re-check timing.

Detector evaluation needs explicit positive and negative examples, an independent definition of the event being detected, and a denominator for each reported rate. A deliberately disabled filter or removed diversity bonus does not guarantee a violation or collapse actually occurs; inspect the resulting condition. Define a separate controlled disagreement case before claiming detection scores for all five types. Undefined correlations from tied or constant predictions, a candidate pool smaller than the planned top 100, and small batches need explicit behavior.

The synopsis says the LLM chooses a repair and parameter, while also saying that candidates are tried cheapest-first and the first valid repair is accepted. These can conflict. Decide who orders or generates candidates, whether the LLM can override the cheapest valid one, and how the no-LLM comparison differs. Continuous parameter ranges also need a finite candidate list or a specified optimization procedure; repair cost constant, ties, allowed no-op behavior and verifier tolerances are still open.

Separate changes to the reward from changes to the predictor and intervals. Changing a reward weight alone need not change prediction correlation or interval coverage, so unchanged checks cannot demonstrate that repair improved those properties. Check rule validity and behavior on known evidence, then measure later outcomes. Rollback retains the old valid rule if no proposed repair passes. Stopping after repeated failures should mean the run stops using its allocated query budget; any request for additional external labels is a separate experiment.

## 8 Fair comparisons and meaningful results

The synopsis commits to random search, greedy predicted-fitness selection, genetic search, AdaLead-style search, Bayesian optimization, a fixed uncertainty penalty and periodic retraining without diagnosis. It also proposes no-LLM and other component-removal comparisons. An ablation is a controlled version with one component removed or changed to test what that component contributes. A finite-pool adaptation of AdaLead or genetic search must be labeled as such; define how it handles a sparse neighborhood with no eligible variants. [1, 14]

Predefine the main comparison: CERA versus fixed uncertainty penalty and retraining without diagnosis, with the same starting data, allowed pool, constraints and maximum budget. Additional baselines help interpret the outcome. Document which methods share the same predictor, retraining frequency and compute allowance. Comparing a more frequently retrained CERA against a less frequently retrained baseline would not isolate the effect of repair.

Measure best observed fitness against the number of new queries, including whether initial examples count. Regret means a gap between the best feasible measured score in a defined pool and the best score found; this is a retrospective pool-specific reference, not a biological global optimum. Define pool eligibility, ties and handling of starting examples before calculating it. The full-pool optimum and top 1% are available to the evaluator only, not the search.

Track predictive interval coverage and width, constraint failures, detector warnings, repairs attempted and accepted, repair costs, rollbacks, stops, runtime and LLM calls. The synopsis defines recovery using a 90% coverage target within five percentage points on a batch of ten: only 9 out of 10 meets that condition. One batch is noisy. Agree on a longer window and a precise failure start, recovery threshold, minimum follow-up and rule for runs that never recover. Treat these as not observed by the end, rather than assigning an invented recovery time.

Use the same initial sets and paired run identifiers where possible and report per-run differences and per-dataset results. Runs on the same dataset are not independent biological datasets. The synopsis proposes confidence intervals and paired statistical tests; with ten runs and a small number of datasets, interpret them cautiously, record ties and zeros, and avoid claims of broad generality. The synopsis's desired 90% coverage and 10% reduction in regret after a failure are targets to evaluate, not achievements.

## 9 Phase by phase roadmap and division of work

The roles below are proposed, not existing assignments. The lead learns, researches, implements and explains the component. The reviewer independently runs checks, challenges assumptions, makes a meaningful contribution and explains it back. Each phase ends in a shared check: merge the evidence, walk through the result together, record decisions and remaining issues, and only then build dependent work. Switch who leads related work in later phases. There are deliberately no dates or duration estimates.

### Phase 1 Evidence and domain foundations

Purpose: understand what each score and protein represents before any experiment depends on it.

Varun leads source verification for amylase, its reference, measurement and position split; Ravi independently checks the source match and mutation counts. Ravi leads IRED source, reference, filtering and mutation-count split, plus Hydro identity and measurement investigation; Varun independently checks the sequence mapping and calculations. Both review GB1 and GFP provenance and licensing, document citations and file hashes, and explain the protein -> assay -> score -> split chain in plain language.

Shared check: a dataset record for every intended experiment lists source version, local path and file fingerprint, score meaning and direction, reference and evidence, split meaning, constraints, counts and unresolved items. Missing metadata blocks the affected experiment or constraint, not the entire project. Confirm whether each person's source evidence supports the other person's calculations.

### Phase 2 Shared experiment rules

Purpose: settle the rules on paper so independent components can be connected without changing the scientific question.

Ravi leads which candidates are allowed, split use, initial measurement selection, budget, query and stopping rules. Varun leads information flow, definitions of the results, fair comparisons and how data are divided for training, interval setting and evaluation. Both decide the primary comparisons, development versus evaluation separation, seed treatment, privacy of label-derived split membership, how repairs are chosen and handling of early stops. Work through two batches by hand, including duplicate and invalid requests.

Shared check: both can trace exactly what is known at each step, how 100 initial and at most 100 new measurements are counted, and what data can affect a decision. The written rules record every deviation from the synopsis and are approved by the team before dependent implementation.

### Phase 3 Restricted experiment runner and ability to repeat the work

Purpose: ensure a selection method cannot accidentally read all measurements and each run can be audited.

Varun leads dataset adapters, stable candidate IDs and the restricted measurement interface. Ravi leads independent tests, run records, deterministic seed handling and budget accounting. Each reviews the other's interface and error cases. Checks cover unknown IDs, repeat requests, budget exhaustion, final partial batch, no eligible candidates, split metadata leakage and replay from a small synthetic dataset.

Shared check: a complete small run exposes only allowed measurements through the selector interface; its saved log independently reconstructs query count, candidates, predictions and decisions. Confirm that the raw files remain outside the selector's supported data interface.

### Phase 4 First fair comparison

Purpose: make an entire experiment work before introducing a complicated model.

Ravi leads random selection and integration with the common runner. Varun leads a simple sequence-based predictor and greedy selection of predicted high scores. Each recreates the other's result from saved settings and inspects whether the same pool, constraints, starting labels and budget were used. Both implement and check an initial best-so-far graph and query ledger.

Shared check: repeated small alpha-amylase runs produce reproducible records and a manually checkable fair comparison. The team can explain why simple results do or do not look plausible without interpreting them as CERA research outcomes.

### Phase 5 Embeddings, predictor ensemble and intervals

Purpose: bring the planned protein representation and uncertainty signals into the same controlled runner.

Varun leads ESM-2 model provenance, representative hardware tests, converting sequences to model input, averaging the outputs and checking saved results. Ravi leads the group of predictors trained on resampled revealed examples, fitting schedule, held-out interval calibration and per-round predictions. Then swap responsibility for testing on a second sequence group. Both verify no padding or special tokens are averaged as residues, cache entries match candidate IDs, and fitting/calibration roles are separate under the agreed experiment rules.

Shared check: a small representative run records the checkpoint and data versions, succeeds on the chosen hardware, and saves predictions and intervals before measurements are revealed. Report observed coverage and interval width without claiming coverage guarantees under adaptive selection.

### Phase 6 Warning definitions and detectors

Purpose: implement the five proposed warning rules and test whether they respond to conditions they are meant to detect.

Ravi leads constraint, support and diversity checks; Varun leads coverage and model-disagreement checks. Both construct positive and negative controlled cases with independently stated expected behavior, including ties, too few candidates, singleton known sets and simultaneous warnings. After initial implementation, swap review and extend one of the other person's tests.

Shared check: for every event, both explain its trigger, timing, inputs, false-alarm scenario and limits on causal interpretation. Every reported detector measure has a defined unit and independent ground truth. Normal operation enforces constraints; faults are injected only in isolated tests.

### Phase 7 Repair and verification

Purpose: decide and implement the smallest allowed, checked response to an event.

Varun leads a finite candidate repair menu, permitted ranges, costs and the initial rule-based selector. Ravi leads verification, unchanged copies of previous versions, rollback, stopping and run records. Together resolve whether repair cost ordering or an LLM choice takes priority, how tie-breaking works, and which evidence each check uses. Test no valid repair, invalid proposed parameters, simultaneous events and repeated failed repairs.

Shared check: a complete rule-based episode can be replayed from the log; the verifier's checks are meaningful for the specific parameter changed; no accepted repair is described as proven effective until future observed outcomes are evaluated.

### Phase 8 Constrained LLM and component comparisons

Purpose: test whether an LLM contributes to an already working non-LLM system.

Ravi leads the restricted goal-to-specification and repair-proposal interface; Varun leads the matched no-LLM comparison and the output-validation checks. Both verify model/provider availability, data handling and pricing at implementation time rather than assuming the synopsis's named service still behaves as described. Record prompt, model/version, parameters, response, validation, retry, fallback, failure and cost. Hosted responses may vary even at low randomness; replay recorded outputs when exact reproduction is needed.

Shared check: invalid output cannot execute code or bypass the allowlist and constraints; no hidden labels enter prompts; the baseline and LLM versions have documented decision rules. Resolve the synopsis conflict between stop-on-invalid specification and retry/fallback before implementation.

### Phase 9 Full evaluation and honest interpretation

Purpose: compare repair with the synopsis's alternatives across the agreed datasets and measure recovery.

Ravi leads remaining comparison methods and verifies their pool, budget and retraining behavior. Varun leads evaluation scripts, ablations, recovery and warning summaries. Swap at least one baseline and one metric for independent review. Both freeze settings after development, run the planned matched repetitions on eligible IRED and Hydro settings, examine per-run and per-protein results, and record failed or stopped runs.

Shared check: all intended comparisons and omissions are documented; outputs can be traced to run records; feasible-pool definitions, costs, early stopping and uncertainty are explicit; negative results are retained. Additional GB1/GFP work happens only after their data and license gates are satisfied.

### Phase 10 Report, application and presentation

Purpose: communicate exactly what was built, measured and learned.

Varun leads an initial draft of the methods and instructions for repeating the work; Ravi leads an initial dataset, results and limitations draft. Then exchange drafts, independently reproduce a representative run and verify every claim against a source or saved output. Both decide whether displaying actual run results in the existing interface adds value and jointly prepare a presentation in which each can explain the whole system, including the other's components. The synopsis lists a paper draft among the deliverables, but also says it depends on whether results are suitable; reinforcement learning is an optional extra comparison. Confirm the paper requirement with the project guide.

Shared check: a new reader can reconstruct a run from recorded source versions, settings and code, understand the comparison, locate raw evidence for each chart, distinguish proposal from result and identify unresolved limitations. Discuss any material departure from the submitted commitments with the project guide.

## 10 Decisions and open questions

1. Agree whether the main candidate pool includes all eligible sequences or only a shifted subset; record when and whether split metadata is visible.
2. Confirm the initial 100 plus up to 100 new labels, 10 repetitions, batch size and validation policy after candidate feasibility checks.
3. Confirm references, score direction and measurement transformations per dataset. Hydro experimental construct provenance and fitness transformation require source-backed validation; IRED's exact steps used to filter the source into the split remains unresolved.
4. Confirm whether Hydro proteins are separate searches and how its score-derived split is disclosed. Establish sufficient eligible seeds after validation exclusions.
5. Choose distance between sequence representations and separate mutation-count rules; define distance limit for the support warning using non-self neighbors, scale, edge cases and units.
6. Define which evidence is used to fit, set intervals, choose repairs and check later results; avoid treating interval-setting data coverage as independent proof.
7. Resolve cost-ordered repairs versus LLM-selected repairs, allowed parameters, tolerance, error retries, fallback and stopping semantics.
8. Freeze the recovery definition, feasible-pool optimum, early-stopping reporting, main measures, paired comparison and uncertainty presentation.
9. Check ESM hardware and model execution, dependency compatibility, provider access and cost. Hardware availability alone is not an inference benchmark.
10. Resolve optional dataset terms before external distribution and confirm with the guide whether any material change to the submitted project scope is acceptable.

## 11 Suggested first shared session

Start with the dataset evidence ledger and the experiment rules, not the user interface. Varun explains the amylase reference and the fact that it appears in the test split; Ravi explains the IRED source match and what remains unknown about filtering. Together trace a two-round run using an invented tiny dataset. Decide who can see each score, which candidates may be queried, how the budget changes and what happens when the first prediction is wrong. The example should contain invented numbers clearly labeled as illustrative.

## 12 Evidence and sources

The local synopsis [1] and briefing [2] are project commitments and explanations, not independent confirmation that the proposed method works. Source code and local checks describe the state on 9 November 2026. Links below identify the sources used; their contents and availability can change. Recheck pinned versions before implementation or redistribution.

[1] Project_Synopsis.pdf, sections 4 to 7, local repository.
[2] Project_Briefing_Guide.pdf, sections 3 and 4, local repository.
[3] Repository README.md, data/SOURCES.md, scripts/download_data.py, scripts/download_optional_data.py and scripts/audit_data.py.
[4] Repository data/USABILITY.md and local raw files. Local audit and file verification rerun 9 November 2026.
[5] FLIP2 benchmark and dataset descriptions: https://flip.protein.properties/ ; archived release v3: https://zenodo.org/records/18433203 .
[6] Original alpha-amylase reference: https://raw.githubusercontent.com/florisvdf/mutation-predictability/main/data/AMY_BACSU/reference.fasta .
[7] Original alpha-amylase sequence and stain activity data: https://raw.githubusercontent.com/florisvdf/mutation-predictability/main/data/AMY_BACSU/combinatorials/data.csv ; original paper: https://pmc.ncbi.nlm.nih.gov/articles/PMC11491678/ .
[8] IRED original lab active data: https://raw.githubusercontent.com/Hollfelder-Lab/lrDMS-IRED/main/data/srired_active_data.csv ; lab data notes: https://raw.githubusercontent.com/Hollfelder-Lab/lrDMS-IRED/main/data/README.md ; original study: https://doi.org/10.1101/2024.04.08.588565 .
[9] Original FLIP GB1 documentation: https://github.com/J-SNACKKB/FLIP/blob/main/splits/gb1/README.md .
[10] ProteinGym score and direction documentation: https://github.com/OATML-Markslab/ProteinGym/blob/main/reference_files/reference_files_description.md ; original GFP study: https://doi.org/10.1038/nature17995 .
[11] Original ESM model and embedding documentation: https://github.com/facebookresearch/esm ; 8M model configuration: https://huggingface.co/facebook/esm2_t6_8M_UR50D/blob/main/config.json .
[12] Fannjiang and colleagues, conformal prediction with feedback-driven shift in biomolecular design: https://pmc.ncbi.nlm.nih.gov/articles/PMC9618043/ .
[13] Lakshminarayanan and colleagues, original deep ensembles paper: https://proceedings.neurips.cc/paper_files/paper/2017/file/9ef2ed4b7fd2c810847ffa5fa85bce38-Paper.pdf .
[14] Ren and colleagues, proximal exploration and sequence design: https://proceedings.mlr.press/v162/ren22a.html ; AdaLead authors' paper: https://arxiv.org/abs/2010.02141 .

[15] Original IRED data archive and fitness description: https://zenodo.org/records/14544486 ; original study dataset: https://zenodo.org/records/11357236 .
[16] UniProt reference sequences used for inferred Hydro alignments: https://rest.uniprot.org/uniprotkb/P06241.fasta ; https://rest.uniprot.org/uniprotkb/P01053.fasta ; https://rest.uniprot.org/uniprotkb/P0A9X9.fasta .

## Appendix A Local file fingerprints

SHA-256 is a fingerprint of file bytes. Matching fingerprints on a later copy provides evidence that the file has not changed, but does not establish that the source data are scientifically correct.

Alpha amylase close_to_far.csv: d04c2fcb7421ffb6ac8b776ed938f7a97c81f8de57f71257d34d9d3722435297
IRED two_to_many.csv: 55425e46a5be5b50fb79dbf8be677422355969da065241e11325a61348e19fae
Hydro low_to_high.csv: 7086f5ad7313c3e572b335d18c378c5bc38fa5ab737820ebed3144749ede4415
GB1 low_vs_high.csv: 190217d19cdafec40d8a961fce2dcbfd9fc89c9f4c6fa994aa90861b06e073fa
ProteinGym GFP assay CSV: 05b97d36a23363331b271edc56f1496b9a539109fd006e65532f91e9903a0838

These fingerprints describe the local extracted files checked on 9 November 2026. They do not pin the remote webpages or model weights.

## Appendix B Short glossary

Assay: a laboratory measurement procedure. For example, testing how much stain a particular enzyme variant removes.
Baseline: a comparison method used to interpret whether a more complex method adds value.
Calibration: using a separate set of known outcomes to adjust a prediction interval; it does not by itself guarantee coverage on adaptively chosen examples.
Candidate pool: the finite set of sequence variants from which this experiment permits a method to choose.
Embedding: numerical features produced from a sequence by a model, here intended to summarize information useful to a predictor.
Evaluation: calculation of agreed results from recorded decisions and measurements. The final evaluator may see information that the selector must not see.
Fitness landscape: the relationship between possible variants and their measured property; this study only observes the variants included in a dataset.
Held-out: examples reserved from a particular fitting or decision step. A measurement revealed to update an adaptive search is no longer held out from later steps of that run.
Mutation limit: a cap on differences from a specified reference, defined only after the reference and counting method are agreed.
Reward: the score used to choose candidates; it may combine model predictions and other terms and is not the experimental measurement itself.
Surrogate: a model used in place of a costly direct measurement; its predictions can be inaccurate.
