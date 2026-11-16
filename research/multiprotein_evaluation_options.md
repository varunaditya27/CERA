# Preparing a multi-protein comparison

This document is a proposal for review. It does not freeze a final protocol, modify code or report search results for IRED or the hydrophobic-core proteins.

## Goal and current capability

The project needs to compare its repair approach against simpler search methods on proteins other than the amylase data used for development. Each method must begin with the same measured examples for a given protein and seed, use the same eligible pool, mutation limit and maximum measurement budget, and report early stops and actual costs. A seed is a number used to reproduce random choices. The three hydrophobic-core proteins must be analyzed separately because they have different sequences and score scales.

The current predictor pilot supports IRED and each hydrophobic-core protein. The existing repeated comparison and random baseline are hard-wired to amylase, and the existing audits and recovery summaries must be checked for their assumptions before reuse. Therefore, running the complete matched comparison requires implementation and tests; simply passing another dataset name to the existing repeated script is not enough. Existing raw files include all scores, so this is an information boundary in the experiment interface, not a security boundary.

## Starting-example choice

The benchmark supplies a train/test split. In IRED, its split is based on number of changes from the reference sequence. In the hydrophobic-core low-to-high split, the train/test assignment is based on the measured scores. If the experiment chooses starting examples from the train side of the latter split, the choice already contains information about scores even when the search code does not read unseen scores.

1. **Score-blind starting examples (recommended primary protocol).** Sample initial measurements from all eligible variants without consulting the train/test or validation flags, and keep all other eligible variants as candidates. This better models a search without advance score knowledge and avoids leaking score-derived Hydro split membership. It does not reproduce the benchmark's original train/test task, and it changes the starting distribution relative to the earlier amylase development comparisons. Every method must share exactly the same initial set, and the result must be called a retrospective finite-pool search, not an official FLIP2 benchmark score.
2. **Original train-side starting examples.** Sample from the published train side, as in the current runner. This is easier to compare with the prior development setup and preserves the benchmark's split membership in the starting data. For Hydro it uses privileged score-derived membership, and its results should not be described as score-blind. It may still be useful as a separately labeled sensitivity analysis, subject to a fixed protocol.

The official [FLIP2 description](https://flip.protein.properties/) identifies the original split designs; the local [Hydro preparation](hydro_preparation.md) documents the score-derived split. Neither choice guarantees unbiased estimates of real-world protein engineering performance, and IRED's local file covers only a subset of the screened variants.

## Proposed implementation steps if score-blind starts are selected

1. Add a clearly specified starting-pool choice to the existing controlled measurement runner, retaining the current default for historical reproducibility. Independently test that the score-blind choice does not depend on split or validation flags, that every method receives identical initial observations, and that budget and duplicate-query checks still hold.
2. Extend the random baseline and a matched comparison runner to dispatch the four protein groups, recording dataset and source fingerprints, the starting rule, seeds, methods and failure or early-stop statuses. Exercise the workflow using synthetic datasets before running evaluation-protein searches. Keep source files and existing run records unchanged.
3. Before interpreting evaluation results, write and review a complete frozen protocol: methods and opt-in repair settings, seeds, predictor and calibration roles, budgets, primary comparison, recovery rule, reporting of incomplete follow-up, Gemini use and costs, and audit procedure. Run the planned matched comparisons only under that reviewed protocol.

This plan describes the implementation direction, not a completed study. A chosen starting-pool rule alone does not settle the final set of methods or the scientific merit of current warning and repair checks.
