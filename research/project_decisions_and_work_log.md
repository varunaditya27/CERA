# CERA decisions and work log

This is the running record for later review. Add dated entries as work proceeds. Distinguish an approved decision from a recommendation, an observation, and an unresolved question. Link supporting evidence and record superseded decisions rather than silently rewriting history.

## Decisions and instructions

| Date | Status | Record |
| --- | --- | --- |
| 2026-11-16 | User instruction | Review the project end to end before implementation; avoid shortcuts and unsupported steps. Ask when clarity is required. |
| 2026-11-16 | User instruction | Maintain a running record of work and decisions for review after project completion. |
| 2026-11-16 | User authorization | Independently review the primary dataset evidence, beginning with amylase, and document findings. This does not approve code changes or experiment design decisions. |
| 2026-11-16 | Approved by Varun | Use all eligible unqueried variants as the candidate pool for the primary experiment. Eligibility constraints and other experiment rules remain open; report selections by original division after the run. |
| 2026-11-16 | Approved by Varun | Keep the amylase reference's measured score hidden until selected under the normal budget. Its sequence can be used to count substitutions. Other datasets' reference treatment remains open. |
| 2026-11-16 | Delegated working choice | Retain the synopsis's 100 initial and up to 100 additional measurements per main run provisionally, pending dataset feasibility and an amylase development pilot before freezing the protocol. User requested the best number be analyzed and selected; optimality is not established. |
| 2026-11-16 | User instruction | Work on a new branch and commit progress as work proceeds. Do not push or open a pull request unless separately requested. |
| 2026-11-16 | User instruction | Use the datasets as source material and make important research-design decisions without constant supervision. Record decisions and evidence. The existing instruction to present a plan and ask before writing code remains in effect. |
| 2026-11-16 | Open | Reference treatment, measurement budget details, split information visible to the search, per-protein Hydro handling, repair selection and recovery definitions require agreement. |

## Work completed

### 2026-11-16: repository and dataset review

- Reviewed the original project briefs, existing research and team roadmaps, dataset documentation, backend catalog, frontend routes and dataset scripts. The research engine and experimental results are not implemented.
- Ran the local dataset structural audit successfully for all five datasets. Verified fingerprints and local gzip/CSV agreement for the three primary datasets.
- Compared amylase and IRED sequence/score pairs with original authors' online tables. Recorded the method, results, source links and limitations in the [primary dataset evidence ledger](dataset_evidence_ledger.md).
- Checked the local Hydro score boundary and counts by sequence length; the full original Hydro archive and experimental reference provenance remain unverified in this review.
- No application code was changed. A complete source-by-source audit and experiment protocol are still in progress; no research outcome is claimed.

### 2026-11-16: split checks and experiment walkthrough

- Pinned the amylase and IRED original repositories to commits and recorded fingerprints for the original comparison tables in the evidence ledger.
- Independently checked that all local amylase split labels agree with the original near-active-site flag and all IRED split labels agree with the two-substitution boundary relative to the uniquely marked original reference sequence. These checks do not resolve IRED filtering or prove how the amylase flag was generated.
- Corrected an initial interpretation of the IRED `WT` field: it marks a row, while that row's `aa_seq` provides the reference sequence. The recorded final counts use the corrected interpretation.
- Added a [two-round experiment walkthrough and decision options](experiment_walkthrough.md). Varun subsequently approved the broad candidate pool; reference treatment and budget policy remain open.

### 2026-11-16: first amylase feasibility check

- Counted local candidates against the pinned original reference under an illustrative four-substitution limit, separately by original split and validation flag. The training side retains at least 1,258 non-validation candidates before any additional exclusions. The limit and validation handling are not approved experiment rules.
- Recorded a recommendation to keep the reference score hidden until it is selected; Varun subsequently approved this for amylase.

### 2026-11-16: measurement budget assessment

- Compared the submitted 100 initial / up to 100 additional budget with the available amylase counts, the need to reserve data for prediction intervals, and the need for multiple opportunities to observe recovery. Documented the working choice and its limitations in the experiment walkthrough.
- No pilot, statistical power study, hardware benchmark, or evaluation-dataset tuning was performed. Batch size, interval-setting allocation, repeat count, and exceptional request handling remain open.

### 2026-11-16: initial data roles

- Reviewed the distinction between fitting a predictor and setting its prediction ranges, including why a range-setting set is not independent proof of its own performance and why adaptive choices complicate coverage claims.
- Counted original train/test and validation flags in all three local primary datasets. Documented candidate allocations and the counts in the [experiment walkthrough](experiment_walkthrough.md).
- Recommend evaluating the synopsis's 80/20 allocation during amylase development, but this is not an approved rule, a demonstrated optimum, or a completed pilot. Allocation and the treatment of subsequently revealed scores remain open.

### 2026-11-16: delegated development protocol

- Following Varun's delegation, selected a provisional amylase development protocol and documented the reasoning, explicit information boundaries, validation roles, budget edge cases and checks in [amylase development protocol](amylase_development_protocol.md). These are development decisions subject to evidence and are not experimental results or a frozen final evaluation protocol.
- The pilot uses 80 initial examples for fitting and model selection and 20 for setting ranges, when interval methods are added. Model selection stays inside the 80; no extra permanent validation group is assumed. Reuse of the 20 and the adaptive search mean formal coverage guarantees must not be claimed without additional justification.
- Prepared a limited implementation plan for a score-controlled runner and meaningful checks. No implementation code has been written; approval is required before starting it.

### 2026-11-16: measurement runner

- Varun approved the runner implementation and requested backend modules remain focused and properly divided. Added `backend/app/amylase.py` for source loading and eligibility and `backend/app/experiment.py` for measurement accounting and run records; the existing catalog remains separate.
- Added the pinned original reference sequence and five focused tests. The tests cover hidden scores through the supported interface, atomic invalid requests, reproducible initial choices, budget and stopping behavior, log reconstruction, and the real local candidate count. The local structural dataset audit also passed; direct catalog health and dataset function checks returned healthy and five entries.
- No predictor, prediction ranges, search method, calibration, repairs, or scientific experiment results are implemented. Python does not provide a security boundary against direct raw-file or object access. An interrupted log write may leave an incomplete record and needs inspection.

### 2026-11-16: first comparison planning

- Reviewed the runner and the next roadmap phase. Found that the supported interface exposes known scores but not their sequences, so a predictor needs a controlled way to obtain both. The current selection record also does not record model predictions.
- Prepared [the first comparison plan](first_comparison_plan.md): matched random selection versus a simple one-hot ridge predictor, with saved pre-reveal predictions and matched starting data. This is a proposed development comparison, not a CERA result.
- Confirmed the current system has scikit-learn, NumPy and SciPy, but the project does not declare them. Version and dependency choices require verification before implementation. No comparison code has been written or run.

### 2026-11-16: first exploratory comparison

- With Varun's approval, exposed revealed sequences, added pre-reveal prediction records, and implemented separate selection and comparison modules. Pinned the tested research dependencies separately from the catalog's requirements. The original model-selection default produced undefined scores on tiny test folds; use negative mean squared error to compare model choices instead.
- Seven unit tests passed with `OPENBLAS_NUM_THREADS=1 PYTHONPATH=backend python3 -m unittest discover -s backend/tests -v`.
- Ran `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend python3 scripts/compare_amylase.py output/amylase_comparison_seed1_final --seed 1`. Both methods started at best observed score 0.1568 with the same initial data; after 100 new measurements the random run reached 0.2116333333333333 and the greedy run 0.1896333333333333. These are one-run exploratory results, not evidence of a general winner.
- Independently checked that initial data, fingerprints and budget settings match; selections precede reveals, no identifier repeats, greedy choices are highest recorded predictions, both stop at budget exhaustion, and the CSV summaries reconstruct from the logs. A repeated run produced identical summary files. Full run records and summaries are in `output/amylase_comparison_seed1_final/`.
- No prediction intervals, CERA failure detection, repairs, language model, repeated-run uncertainty, or evaluation-dataset results are implemented. The original score information remains accessible to processes with direct raw-file access.

### 2026-11-16: repeated-comparison preparation

- Audited the first run after completion: the random method's 100 new choices comprised 49 original-train and 51 original-test variants, while the greedy method chose 100 original-train variants. These labels were joined after the run from the raw file and were not provided as candidate metadata. The observation does not establish the cause.
- Recorded the seeds, pair matching rules, checks and reporting limits for ten additional exploratory pairs in the [repeated-comparison protocol](repeated_comparison_protocol.md), before starting those runs. The seed-1 run is reported separately.

### 2026-11-16: repeated comparisons completed

- Executed ten predeclared amylase pairs with initial seeds 2–11 and independent recorded selection and data-role seed assignments. The greedy run had the higher final best-observed score in nine pairs and random in one; this is descriptive and specific to the development dataset.
- In all ten pairs the greedy method selected zero original-test variants. Random selection chose 49–61 original-test variants in each pair. Original split labels were joined after selection. The cause remains unestablished.
- Independently checked every pair's starting data, settings, selections, pre-reveal rankings, source measurements, budget arithmetic, stop state and reconstructed tables. All 200 method-batches passed the recorded checks. Results and limitations are in [repeated comparison findings](repeated_comparison_findings.md); complete logs and tables are in `output/amylase_repeated/`.
- No implementation code changed for these runs. Prediction intervals, CERA detectors and repairs remain unimplemented; these results are not a final evaluation.
- A post-hoc first-round analysis found higher median predictions for the original-test group in all ten runs despite every top selected variant coming from the original-train group. It also measured how many candidates have substitutions absent from the initial fitting examples. This is exploratory evidence, not a causal explanation; details are in the findings document.

### 2026-11-16: predictor ranking investigation

- Inspected saved rankings across all 100 greedy rounds: the highest-ranked original-test candidate was never above rank 102. In the first round its rank ranged from 313 to 492.
- Reconstructed the seed-2 first-round model from saved settings and verified 100 predictions against the record. The 7,904 position-and-letter indicators absent from the 80 fitting examples had zero fitted coefficients. The relationship between this observation and the observed selection pattern remains unproven. No model or experiment settings were changed.

### 2026-11-16: implementation research review

- Reviewed primary research and official documentation on protein search baselines, uncertainty under adaptive selection, model disagreement, ESM representations, and leakage; mapped the findings to the actual CERA code and remaining decisions in [implementation research notes](implementation_research_notes.md).
- Checked current package metadata and GPU-reported memory. These checks do not demonstrate checkpoint loading, GPU inference or full-dataset feasibility. Recorded an unavailable full-text source and remaining scientific uncertainties explicitly.
- No application code was changed, no model was downloaded or run, and no new experimental performance was claimed.

### 2026-11-16: ESM-2 feasibility check

- Loaded the pinned ESM-2 8M model and tested the amylase reference and a shorter prefix without using any fitness scores. The first GPU inference failed when a native component could not find `Python.h`; an isolated run with `TORCH_DISABLE_NATIVE_JIT=1` succeeded. Avoided an uninitialized pooling layer and documented the loader's unused pretraining-head warning.
- Checked residue-only pooling, output size and finite values, repeat and padding differences, and small warmed GPU batch timings. Exact observations, limits, environment and sources are in [ESM feasibility and plan](esm_feasibility_and_plan.md). These small checks do not establish full-dataset performance or predictive usefulness.
- Prepared a focused representation-module and cache implementation plan. No project application code or dataset was changed; model files were downloaded to the user cache. The prior research-review entry remains historical and describes that earlier review only.

### 2026-11-16: amylase representations

- Varun approved the implementation plan. Added a separate representation module, validated non-pickle cache module, explicit model-check/cache script, separate embedding requirements and lightweight tests. The original catalog and measurement runner remain independent.
- Eleven unit tests passed. A real pinned-model GPU check passed for unequal-length inputs with a maximum padded/unpadded difference of approximately 6.56e-07. Generated and validated a score-free cache of 3,706 x 320 vectors; independently reproduced three earlier-cache vectors and checked a second full generation against the first. Exact commands, hashes, timing, GPU workaround and limitations are in [ESM feasibility and plan](esm_feasibility_and_plan.md).
- No predictor has been fitted with these vectors; their scientific usefulness, CPU behavior, intervals, detectors and repair are unverified. The user model cache was used but not cleared or modified beyond the model download.

### 2026-11-16: prediction-range planning

- Compared first-round nearest-fitting-sequence distances in the saved ESM-2 representation for the ten previous amylase runs. Median distance was higher for the original-test candidates in every run. The split labels were used only for this retrospective description; distance does not establish error or causation. Details and ranges are in the [findings](repeated_comparison_findings.md).
- Researched ensemble fitting, data leakage and adaptive conformal limitations. Prepared a [predictor-group and prediction-range plan](prediction_ranges_development_plan.md), including a bootstrap/cross-validation ordering that avoids placing duplicate copies of one observation across validation folds. This is a proposed initial development design, not a final ensemble or claimed coverage guarantee.
- No new application code or prediction-range experiment was run. The user instruction to ask before writing code applies to the proposed implementation.

### 2026-11-16: prediction-range pilot

- Varun approved the planned implementation. Added focused predictor, interval, cache verification and reporting modules; extended the measurement runner to validate and save pre-reveal candidate ranges. Existing random and one-hot behavior remains available.
- Fifteen unit tests passed. Completed one amylase pilot with 80 initial fitting examples, 20 reserved range-setting examples and 100 later measurements. Independently reconstructed and audited the ten recorded batches and first-round model and range calculation.
- All 100 selected scores were inside their recorded ranges, with mean width approximately 0.20337. The selector chose 34 original-test and 66 original-train variants; those labels were joined only afterward. These one-run observations are not a coverage guarantee, causal attribution, repair result or final evaluation. Details and remaining limitations are in [pilot findings](prediction_range_pilot_findings.md).

### 2026-11-16: research for subsequent work

- Reviewed primary sources on adaptive prediction ranges, uncertainty under shift, warning evaluation with rare events, and the limitations of replay-based comparisons. Mapped the findings and source limits to the current pilot in [next-stage research](next_stage_research.md).
- Reconstructed descriptive pilot errors from saved pre-reveal predictions: mean absolute error 0.051264 for the 100 selected variants and mean range width 0.203374. The pilot contains no interval misses, so it cannot establish a missed-range detector's empirical performance. These are post-hoc descriptions of one adaptive run.
- No application code changed and no new pilot was run in this research step.

### 2026-11-16: repeated range-pilot preparation

- Predeclared ten exploratory amylase range runs, their seed assignments, independent audit checks, score and width denominators, failure handling and lossless record retention in the [repeated-range protocol](repeated_range_protocol.md). The earlier seed-1 pilot remains separate.
- The analysis does not claim independent biological replication or guaranteed 90% coverage. No model or detector settings were changed.

### 2026-11-16: repeated range pilots completed

- Ran all ten predeclared amylase pilots, seeds 2–11. Each exhausted its 100-new-measurement budget; coverage varied from 76/100 to 100/100 and mean widths from approximately 0.1321 to 0.1999. The pooled 899/1,000 is descriptive and does not establish a guarantee.
- Audited all 100 batches against the source records and independently reconstructed every predictor group, selected penalty, reserved-error radius and selected predictions in the same software environment. Preserved complete records losslessly with compressed and uncompressed fingerprints. See [repeated-range findings](repeated_range_findings.md).
- As a separate post-hoc check, the synopsis's below-0.75 coverage rule would have fired in 7 of 80 overlapping three-batch windows. No detector has been implemented or validated, and no causal interpretation is claimed.

### 2026-11-16: warning-check design

- Reviewed the synopsis, current run records and online sources, then specified the five proposed warning conditions, information available before and after reveal, strict boundaries, insufficient-data behavior and controlled test cases in [warning-check design](warning_checks_design.md).
- Identified that current records preserve mean predictions and model spread, but not the five member predictions needed for the proposed Spearman-ranking disagreement rule. Existing models can be reconstructed from recorded inputs and seeds; future real-time checks require explicit pre-reveal evidence.
- The design uses raw Euclidean distance and a specified nearest-other percentile as a provisional development clarification; it does not silently claim the synopsis's normalized-distance implementation is already defined. No warning code, repair or new experiment was implemented in this step.

### 2026-11-16: warning checks and replay

- After Varun approved the plan, implemented five focused development warning rules, pre-reveal member-ranking and distance evidence, post-reveal coverage and support evidence, and a retrospective replay. The measurement runner retains its atomic invalid-request rejection.
- Replayed all ten historical range runs and verified the final warning evidence against an independently audited preliminary replay. Checked all 100 rounds independently, including ranking correlations, distances, Hamming diversity, coverage windows, constraints and source measurements. The below-0.75 coverage rule fired 7 times among 80 eligible overlapping windows; member-ranking disagreement fired in 98 of 100 rounds. Neither count is a validated detection rate or diagnosis.
- Ran and independently audited one fresh warning-enabled seed-12 pilot. Post-hoc first-round inspection found a large difference between ranking agreement over the full pool and the top 100; this motivates further investigation, not a causal conclusion. Results, evidence paths and limits are in [warning-check findings](warning_checks_findings.md).
- Repairs, warning prioritization and the language model remain unimplemented. The retrospective replay requires historical Git commit `78fce61` and the pinned representation cache.

### 2026-11-16: disagreement investigation planning

- Rechecked the historical warning evidence and researched how selection can affect observed associations and how Spearman ranking correlation behaves. The first-round full-pool versus top-100 result remains post-hoc and cannot establish causation or warning accuracy.
- Prepared an [exploratory comparison plan](disagreement_context_plan.md) covering equally sized top, middle, bottom and random candidate groups, reconstruction checks, chronological score access and reporting limitations. Keep the warning and threshold unchanged until independent evaluation is designed. No new analysis or application code was run or written in this step.

### 2026-11-16: disagreement comparison

- Reconstructed all ten historical amylase runs and compared predictor ordering in top, middle, bottom, random and full candidate groups. Every top and random comparison used 100 candidates; all 500 group-round values were available. Average correlations were approximately 0.100, -0.221, 0.221, 0.644 and 0.649 respectively. Results are descriptive and do not establish warning accuracy or causation.
- Checked original record and representation fingerprints, model reconstruction, all candidate predictions, all 100 top-group values against the earlier replay, and first-round values against the previous context table. The backend suite passed 27 tests. The analysis code, records, limitations and reproduction command are in [the findings](disagreement_context_findings.md).
- The existing warning threshold remains unchanged. This analysis does not validate a warning or repair.

### 2026-11-16: reward foundation

- Compared the current implementation with the synopsis and added a separate closed reward-specification validator and deterministic batch selector. Hard constraints filter candidates before scoring; model spread, precomputed normalized distance and nearest-selected sequence diversity are explicit terms. The diversity normalization is a provisional decision documented in [reward foundation](reward_foundation.md), not a validated research setting.
- The backend suite passed 32 tests. A real historical first-round check with zero weights reproduced all ten saved greedy selections among 3,175 candidates. The selector has not yet been connected to an experiment; distance computation, repair and its verifier remain outstanding.
- Updated stale README statements that predated the existing model, range and warning work.

### 2026-11-16: reward pilot and Gemini configuration

- Added a provisional candidate-distance normalization using only known sequences, then connected the checked reward and deterministic batch selector to the amylase pilot. Logged candidate distances, scale, specification and each selection score before reveal. A zero normalization scale is an error rather than a silently substituted value.
- Seed 13 completed ten batches, with 94/100 scores inside their saved ranges and best known score 0.18225. Independently reconstructed all candidate distances and all batch choices, source scores, chronology and budget. The 35-test backend suite passed. Findings, code limitations and losslessly compressed evidence are in [reward pilot findings](reward_pilot_findings.md).
- At Varun's request, checked Gemini configuration without printing the credential. The API model list accepted the key but did not list the configured model spelling; corrected the ignored local configuration to the listed `gemini-3.5-flash-lite`. No generation call or model integration was made in this step. Google's [structured-output documentation](https://ai.google.dev/gemini-api/docs/structured-output) will inform the later constrained interface; output must still pass local validation.
- The pilot has no repair or abstention behavior. The weights, clipping and distance scale are development choices, not validated defaults or evidence of improvement.

### 2026-11-16: Gemini goal compilation and pilot

- Implemented a bounded Gemini request for the fixed fitness goal. It sends no sequence or fitness data, asks only for three weights, validates the resulting specification locally, retries an invalid response once, and records an explicit fallback on failure. Mutation and budget limits remain set by ordinary code. Recorded status and token counts, without storing the key or invalid raw responses.
- The configured Gemini model returned a valid proposal on its first live request (39 input and 39 output tokens). Its saved specification drove a ten-batch seed-13 amylase pilot. An independent audit checked the compiled input fingerprint, all candidate distances and reward rankings, reveal chronology, source scores and budget. The pilot recorded 95/100 covered new scores and best known score 0.18225; these single-run descriptions are not evidence of superiority.
- The 41-test backend suite passed. [Gemini compiler documentation](gemini_goal_compiler.md) records the prompt boundary, fallback, result and remaining gaps. Arbitrary user goals, warning-driven LLM repair, verification and no-LLM evaluation remain unimplemented.

### 2026-11-16: checked repair foundation

- Added a finite, cost-ordered menu of allowed single-weight changes, a verifier and a chooser that retains the original rule if no proposal passes. The verifier checks that specified previously selected items are displaced in a replay, the proposal and constraints are allowed, supplied calibration coverage meets a provisional tolerance, and earlier individual reward rankings do not deteriorate beyond a provisional margin. It marks insufficient or constant-ranking evidence unavailable and does not accept it.
- The 46-test backend suite passed, including a controlled accepted example and rejection for insufficient data, a constant ranking, changed constraints, failure to displace, low coverage, rank deterioration and an exhausted menu. See [repair foundation](repair_foundation.md) for exact decisions and limitations.
- These functions are not yet connected to the experiment. The caller must verify evidence chronology; calibration is reused and unchanged by a reward-only edit. No repair, rollback, abstention or benefit has been demonstrated in a protein run.

### 2026-11-16: integrated repair pilot

- Connected the finite rule-based repair menu and verifier to the amylase reward pilot behind `--repair`. Saved the verifier's interval-setting and earlier-example evidence before each reveal; ordered warnings, rechecked replayed diversity, retained historical warning records, and added a logged early stop that preserves the remaining measurement budget and prevents later reveals.
- The seed-13 pilot stopped after two batches and two failed disagreement-driven repairs, with 80 new measurements unspent. Every proposed weight change failed to displace all flagged selections; no repair was accepted. This is an observation about the strict provisional rules and frequent warning, not evidence that the warning diagnoses error.
- Independently reconstructed both initial selections, candidate distances, six proposed batches, calibration and ranking checks, source measurements and the early stop. The full backend suite passed 50 tests. [Repair pilot findings](repair_pilot_findings.md) documents the warning-target choices, evidence limitations and unresolved work.
- Gemini supplied the initial saved reward weights only; it did not choose repairs. An accepted change was exercised in a controlled test, not in this pilot. Interval-setting data are reused and earlier ranking predictions include training examples, so neither check establishes generalization.

### 2026-11-16: Gemini-assisted repair pilot

- Added a constrained Gemini advisor that receives only the warning type and numbered repair term, weight and cost options. It chooses an option from the existing menu; the normal verifier checks it, then checks remaining options by cost. Invalid choices retry once, and failures fall back to cheapest-first ordering. This explicitly resolves the synopsis's conflicting model-choice and cheapest-first instructions for development.
- In one matched seed-13 pilot, two Gemini calls each selected the middle-cost option; all three options failed verification in each batch. The run retained the old reward and stopped after 20 new measurements with 80 remaining, as in the rule-based pilot. An audit matched both selections and per-weight verification against the independently audited rule-based record, checked sanitized advice and confirmed the key was absent from the run record.
- The 55-test suite passed. Details, usage, assumptions and reproduction are in [Gemini repair pilot](gemini_repair_pilot.md). No repair was accepted, and this single paired development run does not establish model benefit or detector accuracy.

### 2026-11-16: IRED preparation

- Re-fetched the original laboratory active-data table at its recorded commit and verified its fingerprint and single 290-residue reference. Independently matched all 8,586 local sequence/target pairs within 1e-8 and checked split membership against substitution counts. Saved the source-derived reference and confirmed 4,408 train plus 3,225 test variants meet the four-change cap. The 17,143-versus-8,586 source discrepancy remains unresolved.
- Generated and pinned 8,586 score-free, 320-number ESM representations. Regenerated three vectors independently in the same GPU environment with zero observed difference. Added cache validation, IRED dataset dispatch, a measurement-boundary check and a synthetic one-round dispatch test. The full backend suite passed 58 tests. [IRED preparation](ired_preparation.md) records fingerprints, hardware observations and limitations.
- No IRED reward or repair evaluation was run. Treat it as an evaluation dataset and freeze the development rules and matched procedure before interpreting a result.

### 2026-11-16: matched reward comparison

- Predeclared and ran one matched amylase comparison of random, greedy prediction, fixed reward and rule-based repair. The evaluator accessed full-pool scores only after all selectors finished and reported actual measurement counts, finite-pool regret, top-1% membership and available range metrics. All methods shared their initial examples and budget; model-based methods shared role and member seeds.
- Random reached 0.19428 after 100 new measurements; greedy and fixed remained at the shared initial best of 0.18225 after 100; repair remained there and stopped after 20. The initial best was already in the eligible pool's top 1%. These are descriptive one-run observations, not evidence of a general winner or repair effectiveness.
- Independently checked all records, starting data, source scores, query and stopping accounting and reported metrics. The full backend suite passed 61 tests. See [comparison findings](matched_reward_comparison_findings.md) for outputs, limitations and reproduction.

### 2026-11-16: backend package organization

- At Varun's request, moved the flat backend modules into focused `api`, `datasets`, `features`, `experiments`, `rewards`, `llm`, `analysis` and `provenance` packages. Updated imports, tests, scripts and current README examples. Kept `app.main:app` as a compatibility package so existing API startup instructions continue to work.
- Source fingerprints now locate each uniquely named application module within the package tree and reject missing or ambiguous names. Historical replay still reads the original flat file paths from the pinned Git commit; existing records and caches were not rewritten.
- The 62-test suite passed. A historical seed-2 replay matched all 50 prior warning results. Started the compatibility API and verified both endpoints over HTTP, including five available datasets. The real IRED model padding check passed on GPU with maximum observed difference approximately 3.65e-07. These are targeted checks, not a rerun of every experiment.

### 2026-11-16: uncertainty-guided baseline development

- Predeclared and implemented finite-pool mean-plus-spread and Gaussian expected-improvement selection using the same predictor group as the greedy baseline. The Gaussian use of ensemble spread is explicitly an approximation, not a calibrated posterior. Candidate acquisition values are recorded before selection and reveal.
- Both seed-13 amylase runs used the same starting and reserved sets, model seeds and budget as the earlier greedy run. After 100 measurements, the mean-plus-spread run's best observed score was 0.19428 and expected improvement's was 0.18432; the earlier greedy run remained at its initial best of 0.18225. These are one-seed development observations, not a general ranking.
- Independently reconstructed all acquisition scores and selected batches, checked source measurements and budgets, and preserved lossless records. The full backend suite passed 65 tests. [Findings](acquisition_baseline_findings.md) record assumptions, outputs and remaining baselines.

### 2026-11-16: finite-pool evolutionary baselines

- Predeclared and added deterministic finite-pool recombination-and-mutation and AdaLead-style two-step search, with explicit parent selection, predicted-score ordering, two-substitution proximity and a `no_neighbors` stop preserving unspent budget. These are adaptations, not exact implementations of unrestricted algorithms.
- In one matched amylase seed-13 development run, recombination used 100 new measurements and found the eligible pool's maximum score (0.21163). AdaLead-style search used 14 and stopped with no eligible neighbors, reaching 0.18690. The shared initial best was 0.18225. These observations are not a general method ranking or repair evaluation.
- Independently reconstructed every parent and proposal set using mutation-position dictionaries, checked selections, source scores, matching initial settings, budget and stop, and preserved the complete records. The full backend suite passed 71 tests. See [local-search findings](local_search_baselines_findings.md) for methods, outputs and limits.

### 2026-11-16: hydrophobic-core preparation

- Located the original authors' smaller processed GEO table. All 24,935 local sequences uniquely matched it and every local target exactly matched its `fitness_raw` value. All source mutation counts matched the three UniProt reference segments. The source marks a WT row only for P01053, so the other references remain supported by sequence and mutation-count evidence rather than a WT marker.
- Added separate references and verified score-free ESM caches for all three proteins, a common FLIP2 row loader, per-protein measurement access and pilot dispatch. A separate GPU check reproduced one vector per protein within 1.67e-6 absolute difference. The backend suite passed 74 tests, including synthetic dispatch and real cache and budget checks.
- No hydrophobic-core search evaluation was run. The original train/test split is score-derived, so drawing train-side initial measurements is privileged retrospective information. [Hydrophobic-core preparation](hydro_preparation.md) records source links, counts, fingerprints and remaining limitations.

### 2026-11-16: reward selection performance

- Replaced repeated Python sequence-distance loops with an incremental array calculation while preserving the reward formula, constraints and deterministic identifier tie-break. The 75-test backend suite passed.
- Reconstructed all 12 earlier fixed/repair selections and six repair proposal replays. Identifiers and diversity matched saved evidence; rewards matched within 1e-14. The prior and new implementations produced exactly equal output for the first checked batch. The prior batch took about 2.03 seconds versus a new mean of about 0.115 seconds across 12 batches in this environment. See [performance check](reward_selection_performance.md) for limits.

### 2026-11-16: repeated matched development comparison

- Predeclared and ran seeds 21–30 across random, greedy, fixed reward, rule-based repair, Gemini-assisted repair, mean-plus-spread, expected improvement, recombination and AdaLead-style search. All 90 runs completed. The resumable runner records failures and interrupted work without silently replacing them, and evaluates full-pool metrics only after all selectors finish.
- Both repair variants stopped after 20 new measurements in all ten seeds: all 120 proposed changes failed to displace every flagged batch member, and no repair was accepted. Their final best scores matched the fixed-reward runs for every paired seed, despite the latter spending 100 measurements. Recombination reached the eligible pool maximum in 8/10 runs; AdaLead-style search stopped after 0–32 measurements. All initial sets already contained a top-1% variant. These are descriptive results on one protein, not a general ranking or repair validation.
- Independently audited 90 records, 658 selections and 120 repair replays, plus 27 representative local-proposal rounds and six representative distance rounds. A second audit checked 20 successful Gemini advice requests, no fallback and 2,984 reported tokens. The backend suite passed 77 tests before the runs. [Findings](repeated_matched_findings.md) contain all outputs, denominators and limitations.

### 2026-11-16: targeted disagreement development check

- Predeclared and implemented an opt-in rule that builds the disagreement group from the first-choice reward and identifies selected variants with large differences in predictor rank. The existing default remains unchanged. The 0.5 rank-spread cutoff is provisional and does not establish that a prediction is wrong. See [protocol](targeted_disagreement_protocol.md).
- Ran five matched amylase pairs (seeds 31–35). Fixed reward spent 100 new measurements in each; targeted repair stopped after 40, 40, 40, 70 and 30, respectively. Every run's best score was already present in its starting measurements. Two disagreement warnings produced four targeted variants; ten total warning actions retained the current reward and none accepted a change. Results are descriptive and do not establish effectiveness.
- Independently checked source fingerprints, initial measurements, seeds, recorded choices and budget accounting across ten runs and 72 selections; reconstructed 30 repair replays, warning groups, target ranks and pre-reveal recording, and verified all ten summary rows. These checks were one-off read-only commands, not a saved audit program. All 81 backend tests passed before the run. Run records and summary are in `output/amylase_targeted_disagreement_31_35/`. The findings remain exploratory on one protein, and no IRED or hydrophobic-core outcome was used.

### 2026-11-16: diagnosis of targeted repair stops

- Examined all ten failed actions and their 30 proposed changes in the five targeted runs. Every change failed the requirement to remove all flagged candidates; the two diversity actions flagged whole batches. The failure counter carries attempts across rounds and warning types. Documented evidence, limits, relevant research and alternative designs in [the diagnosis](targeted_repair_diagnosis.md). No repair behavior was changed.

### 2026-11-16: retrospective diversity replay check

- Recomputed average pairwise sequence differences for the six rejected diversity proposals from the source sequences. All six met the current warning threshold, despite retaining eight or nine original batch members. The recorded remaining verifier checks also passed. This is a retrospective check of saved replays, not evidence of later-round performance under a changed rule. See [the diagnosis](targeted_repair_diagnosis.md).

### 2026-11-16: retrospective coverage replay check

- Compared saved coverage-warning replays with their pre-reveal ranges and the source dataset's subsequently available scores. Among 18 proposed batches, one had one fewer range miss than the original, 14 had the same number, and three had one more. These post-hoc source scores were not available to the selector and do not establish later-round behavior. See [the diagnosis](targeted_repair_diagnosis.md).

### 2026-11-16: IRED split count source check

- Compared the local IRED file's training, validation and test flags against the authors' published FLIP2 split table. The counts match exactly (3,746, 662 and 4,178; total 8,586), although the same table lists 17,143 overall variants. This supports the local split count but does not establish the filtering chain; see [IRED preparation](ired_preparation.md).

### 2026-11-16: IRED measured-fitness source scope

- The original laboratory's pinned data README describes approximately 11,000 variants with determinable fitness and about 6,000 without measured activity, in separate tables. Previously verified local pairs all match the former table. Documented the resulting selection limitation and the unresolved filtering chain in [IRED preparation](ired_preparation.md).

### 2026-11-16: direct diversity repair check

- With Varun's approval, added an opt-in check that assesses whether the replayed batch resolves the existing diversity warning. It retains the original rule by default, leaves other warnings and verifier checks unchanged, and rejects unavailable evidence. The backend suite passed 83 tests. A separate [comparison protocol](direct_diversity_protocol.md) was recorded before running seeds 41–45.

### 2026-11-16: direct diversity matched development results

- Ran the predeclared five matched pairs for seeds 41–45. The strict and direct runs had identical recorded outcomes and spent 40, 100, 100, 20 and 50 new measurements respectively; three pairs stopped after failed repairs and two exhausted their budgets. One diversity warning occurred in each arm (seed 43); all three proposals still failed the diversity threshold, so no direct diversity repair was accepted. This does not measure the benefit of the earlier six resolved replays or establish equivalent performance generally.
- Independently checked input fingerprints, matching initial measurements and model seeds, 62 selections, 42 repair replays, the direct threshold where invoked, pre-reveal target evidence, scores, budgets and all ten summary rows. These were one-off read-only checks, not a saved audit program. The 83-test backend suite passed before the comparison. Full records are in `output/amylase_direct_diversity_41_45/`; these remain exploratory results for one protein.

### 2026-11-16: direct diversity check on saved examples

- Reconstructed the candidate features, scoring rule, remaining budget, calibration examples and earlier-ranking evidence from the original seed 34 and 35 targeted records. Re-ran both repair modes on each saved diversity warning. The strict mode retained the old rule; the direct mode accepted the first proposed diversity weight, 0.35, with all recorded safeguards passing. Its replayed identifiers exactly matched the original saved first proposal. This verifies the implementation on two retrospectively chosen examples; it does not predict later selections or performance after acceptance.

### 2026-11-16: current README alignment

- Corrected outdated README claims that repair was unimplemented and separate hydrophobic-core protein groups remained undecided. Documented the two opt-in repair checks and linked their development protocols. This updates current guidance without rewriting the historical research notes.

### 2026-11-16: reusable development comparison audit

- With Varun's approval, added `scripts/audit_development_repairs.py` for the two newer comparisons. It reconstructs selections and repair replays independently using saved predictions and distances, checks disagreement group and target evidence before reveal, source and run fingerprints, starting observations, fitting seeds, measurements, budgets and summaries. Average ranks for ties follow [SciPy's documented rule](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.rankdata.html).
- The targeted-disagreement audit passed 10 runs, 72 selections and 30 repair replays; the direct-diversity audit passed 10 runs, 62 selections and 42 replays. A deliberately altered summary and an altered selection with recomputed fingerprints were rejected end to end; new tests also reject altered target and summary evidence. The backend suite passed 85 tests. The audit does not refit predictors, regenerate distances, independently validate every repair safeguard or establish detector accuracy.

### 2026-11-16: evaluation readiness review

- Compared the current implementation and recorded results against the research roadmap. Documented open recovery-metric, repair-evidence, frozen-comparison, multi-protein evaluation and reporting gaps in [evaluation readiness](evaluation_readiness.md). No evaluation-protein search was run and no final method was selected.

### 2026-11-16: recovery measurement options

- Compared one-batch, 30-subsequent-measurement and all-later-measurement summaries, including early-stop handling, dependence and the distinction between a warning and a causal repair effect. Illustrated the options using saved amylase seeds 31 and 34. The 30-measurement definition is a recommendation for review, not an implemented or frozen metric. See [recovery options](recovery_measurement_options.md).

### 2026-11-16: recovery follow-up feasibility

- Checked coverage-warning timing in the 20 recent saved runs. Ten runs warned; three had at least 30 later measurements, seven had ten or fewer, and ten did not warn. The three with sufficient follow-up were fixed-reward runs. This is a feasibility check only, recorded in [recovery options](recovery_measurement_options.md); it does not compare recovery rates.

### 2026-11-16: coverage recovery measurement

- Varun selected the 30-later-measurement option. Implemented a separate read-only summary that validates recorded coverage warnings and chronology, excludes the warning batch, checks 30-measurement windows after later batches and records the first with 26–28 covered scores, its width, follow-up and stop reason. No warning, insufficient follow-up and observed non-recovery remain distinct. The [options document](recovery_measurement_options.md) explains the statistical limitations.
- Applied the measurement to the 20 saved recent amylase runs: two fixed-reward runs reached the band, one fixed-reward run had sufficient follow-up without reaching it, seven runs had insufficient follow-up, and ten had no coverage warning. These development records are not a causal comparison; no later-protein result was used. The backend suite passed 89 tests, including both band boundaries, high coverage, sliding windows, missing follow-up and malformed records.

### 2026-11-16: multi-protein evaluation preparation

- Reviewed current multi-dataset dispatch and identified that the repeated runner and random baseline are amylase-specific. Documented score-blind versus benchmark train-side starting examples and a proposed staged implementation in [multi-protein evaluation options](multiprotein_evaluation_options.md). No final protocol or test-protein search was run.

### 2026-11-16: multi-protein starting-pool feasibility

- Counted eligible sequences without running searches: IRED 7,633 and Hydro groups 1,010, 1,292 and 2,916, each sufficient for 100 starting and up to 100 later measurements. Added row-order invariance to the proposed score-blind starting-pool checks in [evaluation options](multiprotein_evaluation_options.md).

### 2026-11-17: score-blind multi-protein runner preparation

- Varun selected starting examples sampled from all eligible variants. Added this as an explicit `eligible` starting pool while preserving the historical train-side default; sorted identifiers before seeded sampling and recorded the choice. A shared dataset registry now dispatches the random and predictor methods across amylase, IRED and each Hydro protein.
- Added `scripts/run_matched_proteins.py` for explicitly configured, matched methods and seeds. Its manifest pins data, reference, representations, Python, dependencies and code; it records completed, failed and interrupted runs and verifies completed records on resume without silently retrying failures. It does not evaluate full-pool outcomes. The [Python random documentation](https://docs.python.org/3/library/random.html#notes-on-reproducibility) cautions that algorithms can change between versions.
- Synthetic tests confirm score-blind initial identifiers are unaffected by row order, split/validation flags or target changes; random and predictor methods share starts for synthetic IRED and Hydro data. The synthetic matched runner completed and resumed, rejected changed inputs and tampered records, and retained a simulated failure. The full backend suite passed 91 tests. No real IRED or Hydro search was run; the final evaluation protocol and independent multi-protein evaluation are still outstanding.

### 2026-11-17: draft multi-protein comparison

- Drafted a matched four-protein comparison with score-blind starts, separate protein reporting, actual-stop outcomes, recovery follow-up and explicit Gemini/failure accounting. Identified that the current evaluator requires train-side starts and an amylase cache, so a separately tested evaluator and independent audit are needed before real runs. This is a [review draft](multiprotein_comparison_draft.md), not a frozen protocol or completed evaluation.

### 2026-11-17: Gemini model pricing source check

- Checked the configured model name against Google's model and pricing documentation without making an API request. Recorded the published per-token list prices and the fact that actual account tier, quota and future charges remain unknown in the [comparison draft](multiprotein_comparison_draft.md). No credential was recorded.

### 2026-11-17: multi-protein evaluator and independent audit

- Varun selected the full nine-method comparison. Added a score-blind evaluator that checks terminal statuses for every supplied group before loading full-pool scores, verifies starting samples, source and recorded method settings, budgets and measurements, preserves failed/interrupted runs, computes recovery summaries and per-seed differences against fixed reward. Its normal mode requires all four protein groups; a partial report is explicitly labeled development.
- Added a separate audit that reconstructs all recorded random, greedy, acquisition, local-proposal ranking and reward selections and repair replays from saved evidence. It independently reconstructs one available local-proposal round per local method and one reward-distance round per protein, and checks disagreement target chronology. It does not independently refit predictors or validate every warning and verifier assumption. Its normal mode also requires all four groups to reach terminal statuses.
- Synthetic end-to-end tests exercised all nine methods on IRED-format data with a mocked Gemini request, and random and greedy on Hydro-format data. They checked the terminal-status barrier, incomplete and interrupted records, paired missing values, and rejection of altered starts and selections even after fingerprints were recomputed. The full backend suite passed 92 tests. No real IRED or Hydro search or live Gemini request was made. The [comparison protocol](multiprotein_comparison_draft.md) remains a draft until reviewed before real runs.

### 2026-11-17: multi-protein runbook preflight

- Rechecked the four local representation cache fingerprints and proposed output paths; all cache pins matched and no proposed output path existed at that time. Prepared explicit nine-method commands, failure/resume handling and post-run audit/evaluation steps in the [draft runbook](multiprotein_runbook_draft.md). This is not a frozen protocol or authorization to execute; the full workload and provider account quota remain unverified.

### 2026-11-17: Gemini response-accounting preflight

- Compared the current request/response handling with Google's thinking-token documentation. The output limit covers reasoning as well as visible output, and the current client discards returned usage metadata for non-`STOP` responses. Documented that the existing token total may omit rejected requests and is not a billing total in the [comparison draft](multiprotein_comparison_draft.md). No live request or code change was made.

### 2026-11-17: pre-study code review

- At Varun's direction, reviewed changes since `e5a3cc4` against the comparison draft and personal coding standards in separate review axes. Identified missing cross-group code/environment/model matching, incomplete scope and fingerprint enforcement, omitted repair-cost reporting and compressed-file check ordering. Recorded [findings and proposed corrections](multiprotein_code_review.md). No real study runs were started.

### 2026-11-17: repair-cost meaning check

- Checked the implemented repair-menu formula and confirmed that its recorded cost is a dimensionless score for ordering proposed weight changes, not a financial or compute cost. Added the formula and an example to the [pre-study review](multiprotein_code_review.md); no repair or evaluation code was changed.

### 2026-11-17: pre-study review corrections and provider preflight

- With Varun's approval, corrected the review findings: enforced the agreed nine-method, ten-seed, four-group scope and exact reward specification, cross-group code/environment/model consistency, complete predictor-source records and compressed-before-decompressed fingerprint checks. The evaluator now records each dimensionless repair cost and whether it was accepted; the independent audit checks the permitted menu, attempt ordering and fallback choice, and recomputes the cost. Synthetic tests and the full 97-test backend suite passed. See [review](multiprotein_code_review.md).
- Sent one separate synthetic, score-free Gemini repair-menu request as a provider preflight. The configured `gemini-3.5-flash-lite` returned a valid choice on its first attempt and reported 149 input, 10 candidate-output and 159 total tokens. Actual billing and future quota availability remain unknown; this call is not part of any protein-search result.

### 2026-11-17: IRED matched runs completed

- Ran all 90 approved IRED combinations (seeds 51–60 and nine methods) with score-blind starting sets; all reached a completed runner status. The complete compressed records and statuses are preserved under `output/matched_eval_51_60_ired/`. No search outcomes were evaluated or interpreted at this stage; the four-protein audit and evaluation remain pending.

### 2026-11-17: Hydro P06241 matched runs completed

- All 90 approved P06241 combinations reached a completed runner status. Records and statuses are preserved under `output/matched_eval_51_60_hydro-P06241/`. No search outcomes were evaluated at this stage; the four-protein audit and evaluation remain pending.

### 2026-11-17: Hydro P01053 matched runs completed

- All 90 approved P01053 combinations reached a completed runner status. Records and statuses are preserved under `output/matched_eval_51_60_hydro-P01053/`. No search outcomes were evaluated at this stage; the four-protein audit and evaluation remain pending.

### 2026-11-17: Hydro P0A9X9 matched runs completed

- All 90 approved P0A9X9 combinations reached a completed runner status. Records and statuses are preserved under `output/matched_eval_51_60_hydro-P0A9X9/`. At this point all 360 runs have terminal completed statuses; the four-protein audit and evaluation were not yet complete.

### 2026-11-17: four-protein study audit and findings

- All 360 approved runs completed at the runner level. The independent audit reconstructed 2,943 selection batches and 549 repair replays, plus representative local and distance checks. A separate one-off verification checked all 360 summaries and 320 paired differences against source scores and saved records. The audit stdout was transcribed into `output/matched_eval_51_60_audit.json`; its one-off summary verification is not a reusable program.
- Across 40 paired starts, each repair variant had 0 higher, 35 equal and 5 lower final best scores than fixed reward at actual stop. Rule-based repair stopped after failed repairs in 35/40 runs; Gemini-assisted repair in 36/40. Twenty-three repairs were accepted in each arm, and 102 valid Gemini selections and four HTTP 503 fallbacks were recorded. These are finite-pool observations, not proof of equivalence or a causal result. [Findings](multiprotein_study_findings.md) document every protein, baselines, denominators, provider-accounting limits and remaining work.

### 2026-11-17: synopsis completion review

- Compared the original synopsis and briefing guide with the completed study and current research records. Added a [completion evidence review](completion_evidence_review.md) that distinguishes completed evidence from missing split-based evaluation, warning accuracy, component-removal studies, statistical analysis and final deliverables. No new experiment, code change or performance claim was made. The next proposed step is to assess feasibility and design a development-only controlled warning evaluation before implementation.

### 2026-11-17: warning evaluation feasibility

- Reviewed the current five warning implementations, their boundary tests and earlier replay findings. Prepared [a feasibility review](warning_evaluation_feasibility.md) separating rule-correctness checks from prediction of independently defined later outcomes. Identified follow-up censoring, selective measurement and circular labels as limitations; no outcomes, thresholds, new experiments or code were selected or changed.

### 2026-11-17: exploratory later-coverage evaluation

- With implementation approved, defined the [follow-up protocol](warning_followup_protocol.md), implemented a separate evaluator and tests, and analyzed the existing Amylase development replay. The [findings](warning_followup_findings.md) preserve missing follow-up, per-seed counts and the exploratory limitations. A one-off independent source-record calculation checked all 200 later-window rows; the complete backend suite passed 101 tests. No warning threshold was changed and no test-landscape outcome was used for tuning.

### 2026-11-17: exploratory disagreement and ranking

- Implemented the [ranking protocol](disagreement_ranking_protocol.md) for the already approved warning evaluation. The [findings](disagreement_ranking_findings.md) compare saved warnings with separately revealed selected-batch rank correlation without imposing a new failure cutoff. Only two of 100 batches lacked a warning, limiting comparisons. A separate one-off rank calculation checked all 100 coefficients; the backend suite passed 103 tests. No warning, search behavior or test-landscape tuning changed.

### 2026-11-17: controlled warning rule examples

- Added hand-labeled valid, invalid, boundary and unavailable examples for the constraint and diversity rules. All ten constraint cases and five diversity cases matched their expected outcomes. The focused warning tests passed 11 tests and the full backend suite passed 105 tests. [Documentation](controlled_warning_cases.md) separates these rule checks from biological failure detection and cites the existing atomic-rejection integration test.

### 2026-11-17: split evaluation feasibility

- Rechecked FLIP2's split definitions and counted local eligible rows without inspecting scores. Documented [two IRED candidate-pool alternatives](split_evaluation_feasibility.md), the current runner's limitations and Hydro's score-derived split leakage risk. Requested a choice of IRED candidate pool before preparing implementation. No new run or code change was made.
- Inspected the runner, random and local-search methods, evaluator and audit while the pool choice was pending. Documented the need to keep candidate exposure, reveal validation, exhaustion, manifests and independent reconstruction consistent if a restricted mode is selected. No implementation choice or new run was made.

### 2026-11-17: matched-study statistical feasibility

- While the IRED pool choice remained pending, checked the already saved paired outcomes and installed SciPy version. Documented [statistical limitations](matched_statistics_feasibility.md), including ten all-zero pairs for each repair method on P01053, ties on other proteins, differing measurement counts and incomplete recovery follow-up. No p-values, confidence intervals, code changes or additional experimental outcomes were produced.

### 2026-11-17: main-study metric inventory

- Inspected the evaluator and representative compressed record against the synopsis metrics. Updated the [completion review](completion_evidence_review.md) to distinguish top-1% hit from top-1% recall, identify evidence potentially available for cumulative regret and batch metrics, and distinguish retained repair proposals from rollback after later outcomes. This is a record-availability review, not a new analysis of all runs or a claim that missing scientific outcomes can be reconstructed.

### 2026-11-17: independent warning replay calculations

- While the split-pool decision was pending, matched replay hashes against both saved exploratory outputs and independently recalculated 100 support, 100 coverage and 100 disagreement warning statuses. All matched their saved replay records. These one-off checks used recorded distances and member predictions, did not refit models or regenerate distances, and are not reusable audit programs. Updated the corresponding findings with these limits.

### 2026-11-17: repair-policy range coverage reporting

- Aggregated the existing saved coverage counts by protein for both repair policies and independently recomputed all 80 run totals from their fingerprint-checked compressed records. Updated [study findings](multiprotein_study_findings.md) with numerators and denominators. These are whole-run observations, not after-repair causal estimates; the one-off verification was not saved as a reusable audit.

### 2026-11-17: IRED starting-pool choice

- Varun chose to start from variants with at most two substitutions and allow selection from all eligible unmeasured variants afterward. Updated the [split feasibility review](split_evaluation_feasibility.md) and prepared a separate [implementation and study plan](ired_low_change_study_plan.md) for review. No implementation, provider call or new protein-search run was made in this step.
- Independently reconstructed all 4,408 ordered initial-pool identifiers using sequences and split metadata, then checked score-independent sampling for proposed seeds 61–70. Each proposed sample included 13–20 benchmark-validation-flagged variants, consistent with the draft inclusion policy. This was a read-only preflight; the loader read the source table but scores did not determine the samples.
- Checked the pinned IRED cache with its existing verified loader, confirmed the previous reward specification fingerprint and recorded available storage as a point-in-time observation. Did not call Gemini or run the proposed study.

### 2026-11-17: IRED low-change implementation

- Following Varun's full authorization to proceed, added an IRED-only train-start mode to the matched runner and a separately validated study scope to the evaluator and audit. Both reconstruct the exact ordered starting pool; the evaluator reports selected mutation counts. The original four-protein scope still requires all-eligible starts. A synthetic nine-method run with a mocked provider passed evaluation and audit; changed starting-pool order was rejected. All 107 backend tests passed, and re-evaluating the previous 360-run study reproduced its report byte for byte. The [runbook](ired_low_change_runbook.md) records the planned commands and limitations. No new IRED study run was made during implementation.

### 2026-11-17: IRED low-change study completed

- All 90 runs reached completed runner status. The independent audit reconstructed 703 selection batches and 135 repair replays, with one representative distance and two local-proposal checks. An additional one-off calculation verified all 90 recorded summaries and 80 paired differences against source scores and compressed records. Each repair method was higher than fixed reward once, tied seven times and lower twice at actual stop; each stopped after failed repairs in all ten runs. [Findings](ired_low_change_findings.md) distinguish early stops, whole-run coverage, provider accounting and the limits of the exploratory design.

### 2026-11-17: development stopping comparison implementation

- Prepared an isolated Amylase-only comparison of normal repair stopping and continuing after failed repairs, documented in the [protocol](abstention_ablation_protocol.md). Failed proposals remain rejected and constraints remain active; the default policy is unchanged. Added a separate runner and reconstruction audit, synthetic matched-run and stopping tests, and checks that ordinary matched-study evaluation rejects records claiming the stop was disabled. The complete backend suite passed 111 tests; no real development comparison had run at this point.

### 2026-11-17: development stopping comparison results

- All ten Amylase runs completed. The independent audit reconstructed 86 selection batches and 73 repair replays and checked both policies' stopping behavior. Normal stopping ended two of five runs early; continuation found a higher best score in one pair and the same best score in four while using 140 extra measurements in the two early-stopped pairs. [Findings](abstention_ablation_findings.md) preserve per-seed results and explain why this small exploratory comparison does not establish a general or causal benefit.

### 2026-11-17: Gemini response usage accounting

- Checked Google's response and token documentation, then retained valid provider-supplied usage for rejected parsed responses and invalid goal weights across both Gemini call paths. Existing retry, fallback and sanitized status behavior remain. Mocked tests and all 114 backend tests passed; no live call was made. The [accounting note](gemini_usage_accounting.md) preserves the limits: previous missing counts cannot be recovered, some future errors still have no metadata, and logs are not billing records.

### 2026-11-17: additional retrospective metric implementation

- Documented [post-result metric definitions](additional_metrics_protocol.md) and added a separate evaluator for top-1% recall with cutoff ties, cumulative and per-measurement regret, and per-batch sequence difference and prediction-ranking correlation. The terminal-status barrier and existing study checks run before full-pool scores are used. Tests cover tied cutoffs, initial versus new discoveries, short batches, undefined correlations, altered measurements and incomplete studies; all 118 backend tests passed. No extra study outcomes were calculated during implementation.

### 2026-11-17: additional retrospective metric findings

- Evaluated the saved four-protein and separate IRED low-change studies under the post-result definitions. A one-off independent calculation checked top-group counts and recall, cumulative regret and all selected-batch correlations and sequence differences for 450 runs and 3,646 batches. [Findings](additional_metrics_findings.md) show median recall alongside actual top-group sizes and retain unequal-budget, starting-observation and non-independence limitations. No new search or provider request was made.

### 2026-11-17: after-acceptance coverage implementation

- Extended the additional metric protocol and evaluator to identify the first accepted repair and inspect the first 30 later measurements when available. The analysis distinguishes no accepted repair, insufficient follow-up and an observed 30-measurement window; it does not treat the result as causal. Synthetic checks and all 119 backend tests passed. No new after-acceptance outcome had been calculated at this point.

### 2026-11-17: after-acceptance coverage findings

- Applied the post-result first-30-later-measurement definition to both saved studies. Across 100 repair-policy runs, 56 had no accepted repair, six had insufficient later measurements and 38 had complete windows. Independently recomputed all 100 classifications and coverage counts from compressed records and checked previous metric fields were unchanged. [Findings](after_repair_coverage_findings.md) give per-protein denominators and explain why the observations do not establish a causal effect or the original shift-split target.

### 2026-11-17: development evidence-gate comparison implementation

- Prepared the Amylase-only [evidence-gate protocol](verifier_ablation_protocol.md). The experimental mode applies an allowed menu proposal without requiring its evidence verdict, while still calculating that verdict for audit and preserving input, menu, sequence and budget guards. Normal matched-study analysis rejects records with the bypass enabled. Synthetic paired runs, rejected-guard cases and the full 121-test backend suite passed. The earlier stopping-comparison audit was rerun and reproduced its recorded output. No real evidence-gate comparison had run at this point.

### 2026-11-17: development evidence-gate comparison results

- All ten Amylase runs completed; the independent audit checked 69 selections and 60 repair replays. The bypass accepted 30 changes, 29 rejected by ordinary evidence checks, and used 490 new measurements versus 200 for the normal policy. It found a higher best score in one pair and the same best score in four. [Findings](verifier_ablation_findings.md) record individual stops, costs in measurements, and the limits of attributing differences to the gate.

## Next review gates

1. Confirm the remaining dataset provenance and score details, prioritizing amylase for the first experiment.
2. Work through a two-round example and agree on information access, candidate eligibility, measurement accounting and stopping.
3. Define fair comparisons and the checks needed for the first implementation. Seek approval before writing code.
