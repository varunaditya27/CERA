# Dataset-split evaluation feasibility

Reviewed 2026-11-17. This is a design review, not a completed study or a frozen protocol. The [FLIP2 benchmark](https://flip.protein.properties/) defines IRED's two-to-many split using number of sequence changes, and Hydro's low-to-high split using measured fitness. These split types answer different questions.

Imagine a researcher starts with measurements from variants close to a reference protein and wants to choose variants with more changes. The number of changed positions can be calculated from a sequence before measuring its score. In contrast, identifying a variant as belonging to Hydro's above-median-fitness side reveals that its score belongs to a high-score group, even if its exact score stays hidden. A retrospective benchmark can deliberately use such a grouping, but an active search that sees or is constrained by that membership must disclose the privileged information; it is not equivalent to a score-blind search.

## Current local evidence

The existing [four-protein study](multiprotein_study_findings.md) sampled starting observations from all eligible variants without benchmark split labels. It is not a FLIP2 shift-split study. The `Experiment` class can sample initial observations from the benchmark train pool, but the matched-study runner fixes the initial pool to all eligible variants and its candidate pool includes every eligible unmeasured variant. It does not currently enforce an IRED test-side-only candidate pool. Changing only the initial pool would create a different unrestricted search, not the test-side-only design below.

A fresh count using sequences, reference sequences and split fields only, with the existing maximum of four substitutions, found:

| Dataset | Train, non-validation | Train, validation | Test | 
| --- | ---: | ---: | ---: |
| IRED | 3,746 | 662 | 3,225 |
| Hydro P06241 | 223 | 40 | 747 |
| Hydro P01053 | 559 | 154 | 579 |
| Hydro P0A9X9 | 560 | 141 | 2,215 |

The counts are eligible rows, not measured outcomes. For IRED, [preparation checks](ired_preparation.md) found every train sequence has at most two substitutions and every test sequence more than two; the four-substitution cap excludes some test rows. Hydro's score-derived split and construct limitations are described in its [preparation notes](hydro_preparation.md). Using the benchmark's validation rows for starting measurements was allowed in earlier development, but its suitability for a new study should be stated explicitly rather than silently described as official benchmark training.

## IRED study alternatives

**Restrict new measurements to more-changed variants.** Sample the same starting observations for each method from eligible variants with at most two changes, and expose only eligible unmeasured variants with more than two changes as candidates. This directly studies a transition across the mutation-count boundary without revealing hidden fitness. It is a constrained sequential-search adaptation: once a selected variant's score is revealed it can train later rounds, so it is not the original static FLIP2 prediction task. Restriction can change the relative behavior of local-search methods and may leave few neighbors; those stops must be recorded, not concealed.

**Allow every eligible unmeasured variant.** Start from the same low-change pool but let methods also select additional low-change variants. This better represents an unrestricted pool and uses only score-independent information, but a method may never cross the boundary. Report the mutation counts of selections and do not label the entire run a test-side-only comparison.

The first option is recommended for a direct study of the proposed mutation-count shift, provided its constrained pool and sequential retraining are named. The second is a separate question and should not be mixed into the same result table as though the candidate pools were equal.

## Hydro and study safeguards

Do not use Hydro's score-derived membership to restrict a supposedly score-blind selection pool. A separate, explicitly labeled benchmark-style prediction exercise could measure performance on high-score variants, but its score-derived starting partition is privileged retrospective information, and its hidden scores must remain unavailable to the search. That exercise is not yet designed or authorized here.

Before implementation or new runs, define matching starts, methods, seeds, measurement budget, stopping and empty-neighborhood behavior; choose whether benchmark validation rows may be initial observations; predefine scoring and auditing; and account for the fact that the previous IRED/Hydro outcomes have already been inspected. Fresh random seeds on the same datasets do not create an independent protein or erase earlier test exposure. No new scores were inspected and no experiment was run in this review.

## Implementation and audit impact

Read-only code inspection found that a restricted candidate pool would affect more than its initial selection. `Experiment.candidates`, `Experiment.reveal`, and `Experiment.stop_reason` must agree on what is eligible; filtering only the candidates shown to a selector would leave the underlying reveal guard and exhaustion check operating over the larger pool. This is a design risk for a new restricted mode, not a demonstrated defect in the current all-eligible study. The random and predictor-based runners both rely on that interface. Empty candidate pools and local-search methods with no reachable candidates need distinct, recorded stopping behavior.

The existing matched evaluator and independent audit explicitly reconstruct initial observations from the all-eligible pool and reject manifests with another initial-pool setting. Their selection and full-pool optimum checks would need to be defined for the new pool rather than weakened. Study manifests must bind both the initial and candidate-pool definitions, and resume checks must reject changes to either. Synthetic checks should cover attempted selection outside the permitted pool, no score or budget consumed on rejection, exhaustion, identical starts across methods, audit rejection of tampered pools, and continued compatibility with the completed study.

The finite-pool genetic and AdaLead-style methods look for candidates near currently measured sequences; the restricted pool may contain fewer such candidates. The original [AdaLead paper](https://arxiv.org/abs/2010.02141) describes an adaptive greedy sequence-search method, but the local implementation is a finite-pool adaptation and cannot be assumed to behave identically. Record empty neighborhoods and actual measurements for each method before interpreting differences.
