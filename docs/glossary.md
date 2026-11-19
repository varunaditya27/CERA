<div align="center">

# Glossary

Plain-word definitions of the terms used across the project

</div>

Terms are grouped by topic. Where a definition rests on an outside source, the link follows it.

## Proteins and data

- **Amino acid.** One of the 20 building blocks of a protein. A protein sequence is a string of them.
- **Protein variant.** A protein with one or more amino acids changed from a reference sequence.
- **Substitution.** Replacing one amino acid by another at one position. "Four substitutions" means four positions differ from the reference.
- **Reference (wild type).** The original sequence that variants are compared with.
- **Fitness.** The measured quantity the project tries to maximise, such as enzyme activity or stability. Its meaning depends on the dataset.
- **Assay.** The laboratory test that produced a fitness number.
- **Fitness landscape.** All variants of a protein with their measured fitness, seen as a map to search.
- **Split.** A rule that divides a dataset into training and test rows. FLIP2 defines several, such as close-to-far or low-to-high. [FLIP2 benchmark](https://flip.protein.properties/)
- **Alpha amylase (Amylase).** An enzyme that breaks down starch. The development dataset (3,706 rows locally).
- **IRED.** Imine reductase, an enzyme dataset used for evaluation (8,586 rows locally).
- **Hydro.** The hydrophobic-core dataset: three small protein domains (FYN-SH3, CI-2A, CspA) whose fitness is intracellular abundance in yeast, a proxy for stability, analysed separately.
- **Retrospective study.** One that replays already measured data instead of running new laboratory measurements. All CERA results are retrospective.

## Prediction

- **Representation (embedding).** A sequence turned into a list of numbers a model can use. CERA uses 320 numbers per sequence.
- **ESM-2.** A protein language model that produces those numbers. CERA uses the small `esm2_t6_8M_UR50D` checkpoint, kept frozen. [Model card](https://huggingface.co/facebook/esm2_t6_8M_UR50D)
- **Ridge regression.** A simple prediction model that keeps its weights small to avoid unstable fits.
- **Predictor group.** Several models trained together; their disagreement is used as a measure of uncertainty.
- **Mixed predictor.** An experimental group of three ridge models and two small neural networks, developed on Amylase only.
- **Prediction range.** An interval around a prediction that should contain the measured score most of the time.
- **Coverage.** The fraction of measured scores that fall inside their prediction ranges. A 90% range that covers 90% of scores is well calibrated.
- **Calibration.** Setting the width of the ranges using measured examples held back for that purpose.

## Search

- **Search loop.** Predict scores, choose a batch of variants to measure, reveal their scores, update the model and repeat within a budget.
- **Budget.** The maximum number of new measurements a run may make (100 in the main studies).
- **Batch.** The set of variants chosen and measured together (ten in the main studies).
- **Seed.** A number that fixes randomness so a run can be repeated.
- **Starting set.** The variants whose scores are known before the search begins.
- **Greedy.** Always choose the variants with the highest predicted fitness.
- **Fixed reward.** The scoring rule that picks candidates is never changed during the run.
- **Acquisition rule.** The rule that turns predictions into choices. Examples here: mean plus spread (a form of upper confidence bound, UCB) and expected improvement (EI).
- **Genetic and AdaLead-style search.** Evolution-inspired baselines adapted to choose among already measured variants. AdaLead is described in [Sinai et al.](https://arxiv.org/abs/2010.02141)
- **Best observed score.** The highest measured fitness found so far; the main outcome measure.
- **Regret.** The gap between the best score found and the best score available in the eligible pool.

## Reward, warnings and repair

- **Reward.** A scoring rule that combines predicted fitness with penalties and bonuses (distance from known variants, model uncertainty, batch diversity). It is not the measured fitness.
- **Warning check.** A rule that flags a problem, for example measured scores falling outside the ranges, large model disagreement, or candidates far from anything known.
- **Repair.** A bounded change to the reward after a warning, for example raising a penalty weight. Each repair is replayed and verified before it is kept.
- **Evidence gate (verifier).** The check that a proposed repair resolves the flagged problem in a replay before it is accepted.
- **Rollback.** Restoring the previous reward after an accepted repair is followed by poor coverage.
- **Abstention (early stop).** Ending a run after repeated failed repairs instead of continuing.
- **Gemini-assisted repair.** A language model picks among a fixed menu of repairs. Application code validates and verifies its choice, and a local rule is used if the provider fails.

## Reproducibility

- **Fingerprint (SHA-256).** A short code computed from a file's exact contents. If one byte changes, the fingerprint changes. Records store the fingerprints of data, caches and code.
- **Audit.** A script that rebuilds a run's decisions from its saved records and checks them against the fingerprints.
- **Run record.** The log of one run: settings, starting scores, each selection before its result, and the revealed measurements.
- **Cache.** A saved copy of computed sequence representations, so they are not recalculated.
