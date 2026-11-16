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

## Next review gates

1. Confirm the remaining dataset provenance and score details, prioritizing amylase for the first experiment.
2. Work through a two-round example and agree on information access, candidate eligibility, measurement accounting and stopping.
3. Define fair comparisons and the checks needed for the first implementation. Seek approval before writing code.
