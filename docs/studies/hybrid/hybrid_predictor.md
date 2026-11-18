<div align="center">

# Mixed ridge and neural-network predictor

Protocol and findings

</div>

## Protocol

The synopsis proposes an ensemble containing ridge regression and small neural networks. Completed studies used five ridge members, so this opt-in Amylase development implementation adds the missing model type without changing those historical results. It does not assume the new ensemble will perform better.

Use three bootstrap ridge members and two bootstrap neural-network members on the existing fixed 320-value ESM-2 representations. Each neural network has hidden layers of 256 and 128 units with ReLU activations, squared-error loss, and Adam with learning rate 0.001 and weight decay 0.0001, as proposed in the synopsis. For this first implementation, use full-batch optimization, at most 200 epochs and stop after 20 epochs without validation improvement, restoring the best weights. These last settings are development choices, not tuned optimal values.

Each round begins with the existing 20 range-setting examples. From the remaining revealed fitting examples, choose 20% by the round's fixed seed for neural early stopping. This is an internal subset of already revealed data, not an additional dataset split or hidden test set. Choose it **before** bootstrapping, so copies of the same observation cannot cross the neural training/early-stopping boundary. Fit feature and score normalization using only the unique neural training examples, never the early-stopping or range-setting examples. Ridge penalty selection remains cross-validation on the revealed fitting set, and ridge members use that full fitting set; thus neural early-stopping examples can be used by ridge members, but not by the neural networks' own optimization or scaling. No unseen scores enter fitting. The existing range-setting examples remain excluded from all member fitting and model selection.

Train neural networks on the requested device, including the local NVIDIA GPU when CUDA is available; record device, software versions, member seeds, early-stopping and fitting identifiers, epoch counts and training settings. Predict with all five members using the existing ensemble mean and spread. The unchanged range method calculates a 90% nominal radius from the reserved examples. Adaptive selection and small samples do not provide a formal coverage guarantee. [PyTorch Adam documentation](https://docs.pytorch.org/docs/stable/generated/torch.optim.Adam.html) defines the optimizer, and [scikit-learn's leakage guidance](https://scikit-learn.org/stable/common_pitfalls.html#data-leakage) explains why fitted preprocessing must not use held-out data. The [deep ensemble paper](https://papers.nips.cc/paper/2017/hash/9ef2ed4b7fd2c810847ffa5fa85bce38-Abstract.html) motivates comparing multiple predictors but does not establish performance for this implementation.

Initially expose this model only as an explicit Amylase development option. Standard study evaluators and audits must reject it, keeping earlier studies and their model identity separate. Verify finite predictions, unique and disjoint role assignments, correct bootstrap boundaries, normalization without held-out scores, early-stop restoration, CPU reproducibility and actual GPU execution. Run the backend suite. Then run one real GPU Amylase pilot and independently check its score-access chronology and range summaries; report training time, device, stops and limits. A single pilot is a functional check, not evidence the mixed group improves CERA or a comparison on test proteins. Any later comparison must be fixed before its outcomes are inspected and should include actual computation cost.

## Findings

The [development protocol](hybrid_predictor.md#protocol) adds the neural-network members proposed in the synopsis to the existing ridge predictors. It uses three ridge models and two neural networks on the pinned ESM-2 sequence representations. This option is experimental and restricted to Amylase; the completed multi-protein studies used five ridge members and are unchanged.

The 20 range-setting examples remain outside model fitting. Within the remaining revealed fitting examples, an additional 20% is reserved for the neural networks' early stopping. This is an internal part of the same revealed data, not another hidden test split. Neural bootstrap samples and normalization use only the remaining neural training examples. Ridge members use the entire revealed fitting set, including the neural early-stopping subset, but not the range-setting examples. Each round records these roles and member seeds.

### GPU episode

A seed-181 Amylase run with rule-based repair used the NVIDIA GeForce RTX 5050 Laptop GPU. It stopped after two failed repair actions and 20 new measurements. The best measured score remained 0.1719, already present in the initial observations. Recorded ranges covered 18 of the 20 new scores. These small numbers are a functional observation, not evidence of improved search, a calibrated-coverage guarantee or a comparison with the earlier ridge studies.

The run reported approximately 4.03 seconds for the episode in this environment; its two mixed-group fits recorded approximately 1.87 and 0.11 seconds. These values include different initialization overheads and are not a portable benchmark. The [record](../../../output/amylase_hybrid_gpu_seed181_v2/run.jsonl) contains the exact device, software versions, architecture, training settings, fitting roles, early-stopping epochs, predictions, warnings and repair attempts. This episode did not save its neural weights; a later post-episode refit is available as a [development model](model_export.md#findings).

The [audit](../../../output/amylase_hybrid_gpu_seed181_v2_audit.json) checked the two selections, six repair replays, source scores, fitting roles and recorded model settings. It refitted the first mixed group on the same GPU and reproduced all 3,175 candidate means and spreads exactly in this environment. It did not independently refit the second group or establish scientific validity of warnings. A deliberately altered fitting-role record was rejected in a synthetic audit test. All 163 backend tests passed.

An earlier [GPU pilot](../../../output/amylase_hybrid_gpu_seed181/run.jsonl) used the same seed and produced identical recorded ranges and selections, but its implementation could change GPU random state when used on CPU. The corrected implementation seeds only a forked CPU generator for network initialization before moving the network to the chosen device. Tests verify that CPU and GPU random states are preserved for both fitting devices. The first record and its [audit](../../../output/amylase_hybrid_gpu_seed181_audit.json) retain their original source fingerprints; reproduce that audit using its recorded code revision.

### Use and limits

After installing the research and embedding requirements, use a new output directory:

```sh
TORCH_DISABLE_NATIVE_JIT=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend:. python3 -m scripts.amylase.run_reward_pilot output/my-hybrid-run configs/reward_spec_example.json --seed 181 --dataset amylase --hybrid-device cuda --repair --targeted-disagreement --direct-diversity
```

Use `--hybrid-device cpu` for CPU training. A CUDA request fails if CUDA is unavailable. This initial implementation rejects other datasets and combinations with the separate experimental rollback or reactive-calibration modes; ordinary matched-study evaluators also reject it. It has not been compared fairly against the five-ridge ensemble or evaluated on IRED and Hydro. A larger ESM-2 embedding model was not used. These limitations should be resolved by a prespecified comparison before any claim that the neural members improve the system.
