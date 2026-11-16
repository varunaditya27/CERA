# First reward-based amylase pilot

Completed 16 November 2026. This is one development run on the amylase dataset, not an evaluation of CERA's repair procedure or evidence that the reward improves search.

## How the run chose variants

The existing five-predictor group supplied a predicted score and model spread for each candidate. The reward subtracted weighted spread and distance, then added weighted sequence diversity within the batch. The checked-in [example specification](reward_spec_example.json) uses the synopsis's illustrative weights, which are not tuned or validated. Hard mutation limits remained filters.

Distance means straight-line distance between the ESM representations, not a count of amino-acid changes. For each previously measured sequence, find the distance to its nearest **other** previously measured sequence; the largest of these distances is the scale. Divide each candidate's distance to its nearest previously measured sequence by that scale, and cap the result at one. This uses no hidden measurements, but distances at or above the scale become indistinguishable. If the known representations give a zero scale, the run rejects the calculation instead of inventing a value. This max-based scaling is a provisional choice because the synopsis does not specify a normalization; its sensitivity and scientific value remain unvalidated. Representation-space similarity depends on the chosen representation, as discussed in [Carr et al. (2024)](https://pmc.ncbi.nlm.nih.gov/articles/PMC11095727/).

The run records the specification, all candidate distances, scale, predictions, and sequential reward scores before revealing each batch. Distance input uses the known sequences, not the next batch's hidden scores. It retains the existing warning calculations, which use a separate raw-distance threshold. The exact code, data and representation fingerprints are recorded with the run.

## Observations and checks

Seed 13 began with 100 measured variants and selected 100 more in ten batches. The saved prediction ranges contained 94 of the 100 subsequently revealed scores; the best score among the 200 known at the end was 0.18225. The distance cap applied to approximately 1.4%–1.5% of candidates per round. These are descriptive observations of one adaptive run, without a matched comparison or coverage guarantee.

An independent audit reconstructed all ten selection steps using a separate vectorized calculation, recalculated every candidate distance from the pre-batch known set, checked reward scores and selection order, confirmed the score reveal matched the source, and checked chronological ordering and budget arithmetic. The full backend suite passed 35 tests, including known-distance examples, zero scales and invalid inputs. The losslessly compressed record, fingerprints, coverage table and audit summary are in [the output directory](../output/amylase_reward_pilot_seed13/).

To reproduce with a new output directory and the pinned representation cache:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend python3 scripts/run_reward_pilot.py output/my-reward-pilot research/reward_spec_example.json --seed 13
```

The run does not repair or revise its reward, and the abstention field is validated but not acted on by this pilot. No language-model call was made. A matched comparison, meaningful verification rules, repair and independent evaluation remain required.
