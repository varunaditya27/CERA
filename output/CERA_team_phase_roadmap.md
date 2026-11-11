# CERA Team Roadmap

A working guide for Varun and Ravi

Goal: build and test a system that spots when protein fitness predictions mislead a search, then checks whether an allowed change helps the search recover. The experiments use previously measured variants; they are not new laboratory tests.

## How to use this guide

The person listed as lead takes the first pass and explains the work. The other person checks it, runs it and helps improve it. Switch roles on related work so both of you learn the whole project. At the end of each phase, complete the shared check together and record any open questions. The assignments are a proposal and can be rebalanced.

## 1  Understand the datasets

**Purpose: **Confirm what each score means, how the original protein is identified, and how the data were divided.

**Varun leads: **Check alpha amylase and its original reference sequence.

**Ravi leads: **Check IRED and Hydro, including the three proteins in Hydro.

**Deliverable: **Dataset notes with sources, verified facts, and unanswered questions.

**Shared check: **Each person explains the other’s findings. Confirm that the IRED filtering and Hydro reference details still needing evidence are marked as open.

## 2  Agree on the experiment rules

**Purpose: **Decide what information the search can see, which variants it may choose, how measurements are counted, and when a run stops.

**Ravi leads: **Draft the candidate, measurement budget, and stopping rules.

**Varun leads: **Draft the rules for hidden scores, fair comparisons, and how results will be measured.

**Deliverable: **A short written experiment plan and a hand-worked example.

**Shared check: **Trace two rounds together. The synopsis proposes 100 starting measurements and up to 100 more; confirm this and candidate availability before fixing the plan.

## 3  Build the experiment runner

**Purpose: **Create the part that loads variants, reveals only requested scores, counts requests, and saves what happened.

**Varun leads: **Lead data loading and the controlled score-reveal interface.

**Ravi leads: **Lead checks for repeated requests, invalid variants, exhausted budgets, and saved run records.

**Deliverable: **A small experiment that can be repeated from its saved settings.

**Shared check: **Run a tiny example together and check that the search cannot obtain hidden scores through its normal interface.

## 4  Make the first comparison

**Purpose: **Run two simple approaches: pick variants at random, and pick variants with the highest predicted scores.

**Ravi leads: **Lead random selection and connect it to the runner.

**Varun leads: **Lead a simple prediction model and score-based selection.

**Deliverable: **The first comparison, a list of selected variants, and a graph of the best score found.

**Shared check: **Check that both approaches start with the same information and use the same rules and measurement budget.

## 5  Add the planned prediction models

**Purpose: **Use ESM-2 to turn each protein sequence into numbers, then train several models and estimate how uncertain their predictions are.

**Varun leads: **Lead the sequence-to-numbers step and test it on the available computer.

**Ravi leads: **Lead the group of prediction models and the ranges around their predictions.

**Deliverable: **Saved sequence representations, predictions, and uncertainty ranges for a small run.

**Shared check: **Check that predictions are saved before scores are revealed. Test model execution and memory use; the hardware has not yet been tested with the full model.

## 6  Detect problems

**Purpose: **Create checks for broken limits, unfamiliar candidates with prediction misses, unreliable prediction ranges, model disagreement, and overly similar batches.

**Ravi leads: **Lead checks for limits, unfamiliar candidates, and batch similarity.

**Varun leads: **Lead checks for prediction ranges and model disagreement.

**Deliverable: **Five warning checks with examples that should and should not trigger them.

**Shared check: **Explain what each warning means and when it could be wrong. A warning alone does not prove the cause of a bad prediction.

## 7  Repair the scoring rule

**Purpose: **When a warning appears, try a permitted change, check it against the agreed rules, and keep or reject it.

**Varun leads: **Lead the list of allowed changes and the rule for choosing between them.

**Ravi leads: **Lead the checks, restoration of the previous rule, stopping behavior, and records.

**Deliverable: **A working repair process and a record of each proposed and accepted or rejected change.

**Shared check: **Replay one failure together. A repair passing checks does not prove it will improve later results.

## 8  Add the language model

**Purpose: **Test whether a language model helps propose settings or repairs within the permitted rules.

**Ravi leads: **Lead the restricted language-model interface.

**Varun leads: **Lead the comparison with the rule-based version and checks on model outputs.

**Deliverable: **A language-model version, a rule-based version, and records of their decisions.

**Shared check: **Confirm that hidden scores are never sent to the model and that invalid responses cannot bypass the rules.

## 9  Run the full evaluation

**Purpose: **Compare CERA with the agreed alternatives on the prepared datasets, using repeated runs and the same starting information and budget.

**Ravi leads: **Lead the remaining comparison methods and check their budgets.

**Varun leads: **Lead result calculations, charts, and checks of whether the search recovered after failures.

**Deliverable: **Results for each dataset, comparison charts, and a record of failures and stopped runs.

**Shared check: **Review the results independently, then compare interpretations. Report negative results and explain any work left out.

## 10  Prepare the report and presentation

**Purpose: **Explain what was built, how the experiments worked, what the results show, and what remains uncertain.

**Varun leads: **Draft the method and instructions for repeating a run.

**Ravi leads: **Draft the dataset, results, and limitations sections.

**Deliverable: **Final code, report, results, and presentation.

**Shared check: **Exchange drafts, independently repeat a representative run, and practise explaining the whole project to someone new.

## Start here

Begin with Phases 1 and 2. Review the existing dataset findings, divide the remaining checks, and agree on the experiment rules before writing experiment code. Keep the detailed roadmap nearby for the evidence and decisions behind this shorter guide.

## Reference

Detailed research and project roadmap: research/CERA_research_evidence_and_roadmap.md. A PDF and Word version of that document are in the output folder.
