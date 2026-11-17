# CERA: integrated project status and results

**Status: working research prototype; scientific evaluation and final deliverables remain incomplete.** This report brings together the current implementation and results as of 17 November 2026. It does not replace the [decision and work log](project_decisions_and_work_log.md), [completion evidence review](completion_evidence_review.md), or individual study records.

## The problem and the approach

A protein variant is a modified amino-acid sequence. Measuring its activity or stability in a laboratory can be expensive, so a model predicts scores and a search chooses which variants to measure next. CERA investigates whether the search can detect warning signs and safely change its scoring rule when predictions and observations disagree.

The prototype uses previously measured datasets to simulate measurements. An optional [Amylase development policy](reactive_calibration_findings.md) updates range-setting examples after a coverage warning; it is not part of the completed evaluation studies and has no adaptive-coverage guarantee. It converts sequences into numerical representations with a frozen ESM-2 model, fits a group of five regression models (or an experimental Amylase-only group with three ridge models and two neural networks), calculates prediction ranges, and selects candidates using predicted fitness, uncertainty, distance from known variants and batch diversity. It records measurements, warnings, proposed changes, checks and stopping. Gemini can propose bounded weights or prioritize a fixed repair menu; application code validates proposed changes. Raw source files remain accessible to someone with file access: the measurement interface prevents accidental disclosure through its API, not adversarial access.

## Data and comparisons

| Source | Use in this project | Local rows | Important limitation |
| --- | --- | ---: | --- |
| Alpha amylase | Development and checks | 3,706 | Results are retrospective measurements, not new laboratory experiments. |
| IRED | Evaluation, mutation-count split | 8,586 | The local split is a subset of a larger screened collection; filtering provenance is incomplete. |
| Hydro | Evaluation, three separately analyzed proteins | 24,935 | Its low-to-high split is based on measured fitness, so using membership reveals privileged information. |

Source identities, original publications, references and licenses are in the [dataset ledger](dataset_evidence_ledger.md), [IRED preparation](ired_preparation.md), [Hydro preparation](hydro_preparation.md) and [source list](../data/SOURCES.md). The [FLIP2 benchmark](https://flip.protein.properties/) describes the split definitions. The research compares random, greedy, fixed reward, rule-based repair, Gemini-assisted repair, mean-plus-spread, expected improvement, finite-pool genetic and AdaLead-style search. The latter methods are adapted to the available measured pool. Models are retrained before each batch for the applicable model-based methods.

## What the completed studies show

- **Four-protein, unrestricted starts:** 360 runs completed. Against fixed reward at each method's actual stop, each repair policy had 0 higher, 35 tied and 5 lower best scores across 40 paired starts. Rule-based repair stopped after failed checks in 35 runs and Gemini-assisted repair in 36. Fixed reward used its full 100-measurement budget in all runs. [Results and audit](multiprotein_study_findings.md).
- **IRED, low-change starts:** 90 runs completed. Each repair policy was higher in one pair, tied in seven and lower in two; both stopped after failed repairs in all ten runs. Each used 410 new measurements in total versus 1,000 for fixed reward. Later candidates came from the entire eligible pool. [Results and audit](ired_low_change_findings.md).
- **Hydro, low-fitness starts:** 270 runs completed. Each repair policy was lower in 25 of 30 pairs and tied in five at its actual stop. Each used 1,130 new measurements versus 3,000 for fixed reward; 27 of 30 runs stopped after failed checks. A later comparison at the same measurement count gave 30 ties per repair policy. The starting pool uses the benchmark's score-derived membership, and later candidate access is unrestricted. [Results and audits](hydro_low_fitness_search_findings.md).
- **Held-out static prediction:** Median range coverage was 90.0% for IRED and 0.0%, 11.7% and 10.6% for the three Hydro proteins. These are medians over ten starts, not formal coverage guarantees. The Hydro split is score-derived and the study excludes variants above four substitutions. [Results and audit](heldout_shift_prediction_findings.md).

The above starts reuse fixed protein datasets. They are not independent biological replications. Comparisons at actual stop include different measurement counts and do not isolate the effect of changing the reward from the effect of stopping. Equal best scores do not prove the policies are equivalent.

## Why repairs stopped

In the Hydro low-fitness study, both repair policies stopped after consecutive failed actions in different batches in all 54 early-stopped policy runs. Across both policies, 357 proposed changes were rejected. Every rejected proposal failed either the check that all flagged candidates disappeared in a replay or the direct diversity-resolution check. Some also failed ranking preservation. These are properties of the implemented checks, not proof that the rejected or replacement candidates would be better. The stored calibration check uses existing intervals and cannot itself show that a changed reward improves future coverage. [Diagnosis and audit](hydro_repair_stopping_diagnosis_findings.md).

## What is implemented and how to run it

- The web workspace is in `frontend/` and `backend/app/api/`. It shows dataset information and the pinned mixed-predictor development comparison, and predicts eligible Amylase sequences using the exported development model and verified local representation model; it also runs bounded local experiments across Amylase, IRED and three hydrophobic-core proteins using fixed reward, rule-based repair or optional Gemini-assisted repair. Completed local runs have a batch-by-batch review of revealed measurements and recorded decisions.
- The experimental pipeline is in `backend/app/experiments/`, `features/`, `rewards/`, `llm/`, `analysis/` and `provenance/`. It runs from scripts and writes local records.
- `scripts/compile_reward_goal.py` can accept optional user goal text through `--goal`. The text is sent to Gemini and saved. The model can misunderstand it; review the bounded specification before use. The only supported objective is maximizing the dataset fitness score. [Goal compiler](natural_goal_compiler.md).
- `scripts/run_reward_pilot.py` consumes a saved specification. `--repair` enables rule-based repair, and `--gemini-repair` lets Gemini select among permitted repairs. The [README](../README.md) covers setup and study commands.

Verification in this checkout includes 175 passing backend tests, a production frontend build, HTTP checks against a live local backend, and a live Gemini goal-to-Amylase episode. The local RTX 5050 is visible to PyTorch; the existing sequence representations were generated using the GPU. A fresh offline GPU check reproduced finite 320-value vectors, with a maximum padding difference of 6.56e-7. The [mixed predictor GPU pilot](hybrid_predictor_findings.md) was functionally audited; its exported model has an [exploratory Amylase prediction comparison](exported_model_evaluation_findings.md), and an [exploratory matched search comparison](mixed_search_comparison_findings.md) has been replay-audited. It has not been evaluated on test proteins. A larger embedding model has not been evaluated, and no claim is made that it would improve results. The web check did not exercise browser interaction or deployment.

## Evidence that remains missing

1. A test-only sequential shift study and independent biological validation of the warning types. The existing static split check and unrestricted searches answer different questions.
2. Stronger evidence about reverting an accepted reward: the [later-rollback development check](later_rollback_findings.md) implemented and tested the mechanism, but no real run triggered it. Some repair-removal and universal-penalty comparisons also did not exercise their interventions.
3. An independent causal estimate of repair benefit or proof that the proposed after-repair coverage and regret targets were met. Some runs stop before enough later observations are available.
4. Independent evaluation of the mixed predictor beyond the [matched development searches](mixed_search_comparison_findings.md) and its [post-episode development model](hybrid_model_export_findings.md). A final presentation and, if warranted by the results, a paper draft are also outstanding. The web runner supports only local simulations with the fixed project specification and is not a complete experiment-management interface.

The [completion evidence review](completion_evidence_review.md) provides the detailed requirement-by-requirement limitations. Provider token counts in study records are not verified billing. Larger models, new tests and new methods must be evaluated without using evaluation outcomes to tune the procedure and without presenting exploratory findings as confirmation.
