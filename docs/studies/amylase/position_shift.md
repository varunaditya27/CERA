<div align="center">

# Amylase position-shift check

Findings

</div>

The FLIP2 close-to-far split places mutations near the enzyme's active site on the training side and farther-away mutations on the test side. The earlier Amylase search could select from both sides. This static check holds the far side aside throughout fitting and range setting. [FLIP2 split definition](https://flip.protein.properties/) · [Earlier searches](repeated_comparison.md#findings)

The check reused the five-ridge held-out protocol and starting seeds 121–130. The four-substitution cap left 1,566 eligible training-side examples and 1,709 test-side examples. For each start, 100 examples were sampled using the training-side pool in its original file order. Eighty were used for fitting and twenty for setting prediction ranges. As in the earlier static checks, validation-marked training-side rows were eligible. The predictor received only the selected training scores. All ten runs produced their predictions before the evaluator compared them with test scores. [Existing held-out protocol](../hybrid/heldout_shift_prediction.md#protocol)

Median coverage was **90.2%**, with a range of **65.7–98.0%** across starts. Median absolute error was **0.05118** in the source score units. Median Spearman rank correlation was **0.0005**, indicating little agreement between predicted and measured order at the median start. Coverage and ranking answer different questions. These ten starts reuse one development dataset. They give an exploratory capped comparison, without a formal coverage guarantee or evidence about repair. [Machine-readable results](../../../output/amylase_position_shift_121_130.json)

Reproduce the result from the repository root using the checked-in representation cache and a new output path. A second run reproduced the report byte for byte, including the fingerprint of the predictions.

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend:. python3 -m scripts.heldout.evaluate_amylase_position_shift output/my-amylase-position-shift.json
```
