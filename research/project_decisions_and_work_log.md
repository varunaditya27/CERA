# CERA decisions and work log

This is the running record for later review. Add dated entries as work proceeds. Distinguish an approved decision from a recommendation, an observation, and an unresolved question. Link supporting evidence and record superseded decisions rather than silently rewriting history.

## Decisions and instructions

| Date | Status | Record |
| --- | --- | --- |
| 2026-11-16 | User instruction | Review the project end to end before implementation; avoid shortcuts and unsupported steps. Ask when clarity is required. |
| 2026-11-16 | User instruction | Maintain a running record of work and decisions for review after project completion. |
| 2026-11-16 | User authorization | Independently review the primary dataset evidence, beginning with amylase, and document findings. This does not approve code changes or experiment design decisions. |
| 2026-11-16 | Approved by Varun | Use all eligible unqueried variants as the candidate pool for the primary experiment. Eligibility constraints and other experiment rules remain open; report selections by original division after the run. |
| 2026-11-16 | User instruction | Work on a new branch and commit progress as work proceeds. Do not push or open a pull request unless separately requested. |
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
- Recorded a recommendation to keep the reference score hidden until it is selected; Varun has not yet approved this recommendation.

## Next review gates

1. Confirm the remaining dataset provenance and score details, prioritizing amylase for the first experiment.
2. Work through a two-round example and agree on information access, candidate eligibility, measurement accounting and stopping.
3. Define fair comparisons and the checks needed for the first implementation. Seek approval before writing code.
