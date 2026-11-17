# Mixed ridge and neural predictor: GPU pilot

The [development protocol](hybrid_predictor_protocol.md) adds the neural-network members proposed in the synopsis to the existing ridge predictors. It uses three ridge models and two neural networks on the pinned ESM-2 sequence representations. This option is experimental and restricted to Amylase; the completed multi-protein studies used five ridge members and are unchanged.

The 20 range-setting examples remain outside model fitting. Within the remaining revealed fitting examples, an additional 20% is reserved for the neural networks' early stopping. This is an internal part of the same revealed data, not another hidden test split. Neural bootstrap samples and normalization use only the remaining neural training examples. Ridge members use the entire revealed fitting set, including the neural early-stopping subset, but not the range-setting examples. Each round records these roles and member seeds.

## GPU episode

A seed-181 Amylase run with rule-based repair used the NVIDIA GeForce RTX 5050 Laptop GPU. It stopped after two failed repair actions and 20 new measurements. The best measured score remained 0.1719, already present in the initial observations. Recorded ranges covered 18 of the 20 new scores. These small numbers are a functional observation, not evidence of improved search, a calibrated-coverage guarantee or a comparison with the earlier ridge studies.

The run reported approximately 4.03 seconds for the episode in this environment; its two mixed-group fits recorded approximately 1.87 and 0.11 seconds. These values include different initialization overheads and are not a portable benchmark. The [record](../output/amylase_hybrid_gpu_seed181_v2/run.jsonl) contains the exact device, software versions, architecture, training settings, fitting roles, early-stopping epochs, predictions, warnings and repair attempts. This episode did not save its neural weights; a later post-episode refit is available as a [development model](hybrid_model_export_findings.md).

The [audit](../output/amylase_hybrid_gpu_seed181_v2_audit.json) checked the two selections, six repair replays, source scores, fitting roles and recorded model settings. It refitted the first mixed group on the same GPU and reproduced all 3,175 candidate means and spreads exactly in this environment. It did not independently refit the second group or establish scientific validity of warnings. A deliberately altered fitting-role record was rejected in a synthetic audit test. All 163 backend tests passed.

An earlier [GPU pilot](../output/amylase_hybrid_gpu_seed181/run.jsonl) used the same seed and produced identical recorded ranges and selections, but its implementation could change GPU random state when used on CPU. The corrected implementation seeds only a forked CPU generator for network initialization before moving the network to the chosen device. Tests verify that CPU and GPU random states are preserved for both fitting devices. The first record and its [audit](../output/amylase_hybrid_gpu_seed181_audit.json) retain their original source fingerprints; reproduce that audit using its recorded code revision.

## Use and limits

After installing the research and embedding requirements, use a new output directory:

```sh
TORCH_DISABLE_NATIVE_JIT=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend python3 scripts/run_reward_pilot.py output/my-hybrid-run research/reward_spec_example.json --seed 181 --dataset amylase --hybrid-device cuda --repair --targeted-disagreement --direct-diversity
```

Use `--hybrid-device cpu` for CPU training. A CUDA request fails if CUDA is unavailable. This initial implementation rejects other datasets and combinations with the separate experimental rollback or reactive-calibration modes; ordinary matched-study evaluators also reject it. It has not been compared fairly against the five-ridge ensemble or evaluated on IRED and Hydro. A larger ESM-2 embedding model was not used. These limitations should be resolved by a prespecified comparison before any claim that the neural members improve the system.
