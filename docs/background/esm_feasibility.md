<div align="center">

# ESM-2 feasibility check and implementation plan

Feasibility note

</div>

Checked 16 November 2026. This is a small engineering check, not a protein-fitness experiment or proof of full-dataset feasibility. No dataset scores were read during model inference. The 57-residue input below was a prefix of the amylase reference used to test unequal sequence lengths; it is not asserted to be an independent biological construct.

## Model and environment

- The checkpoint is [`facebook/esm2_t6_8M_UR50D`](https://huggingface.co/facebook/esm2_t6_8M_UR50D) at revision `c731040fcd8d73dceaa04b0a8e6329b345b0f5df`. The [model configuration](https://huggingface.co/facebook/esm2_t6_8M_UR50D/blob/c731040fcd8d73dceaa04b0a8e6329b345b0f5df/config.json) specifies 320 hidden features.
- Local versions: Python 3.14, PyTorch `2.14.0+cu130`, Transformers `5.16.1`, NVIDIA RTX 5050 Laptop GPU. PyTorch reported CUDA available. Model files were downloaded to the normal user cache; they were not committed.
- Loading `AutoModel` with its default pooling layer produced missing pooling-layer weights; those newly initialized weights should not be treated as pretrained. Reloading with `add_pooling_layer=False` avoided those missing weights. The loader still reported unused masked-language-model head weights, consistent with loading the base representation model rather than the pretraining head. The checked representation uses `last_hidden_state`, not the discarded head or a randomly initialized pooler.

## GPU issue and tested fallback

The first inference attempt failed with `fatal error: Python.h: No such file or directory` while PyTorch's native GPU path tried to compile a Triton component. `torch.cuda.is_available()` being true did not reveal that failure. For the second attempt, setting `TORCH_DISABLE_NATIVE_JIT=1` for that process allowed inference to complete. This is an environment-specific tested workaround, not proof all GPU workloads work or an instruction to silently modify the user's system. PyTorch also documents controls for its [Python native backends](https://docs.pytorch.org/docs/stable/backends#module-torch.backends.python_native). No system packages were installed.

## Representation checks

The reference sequence had 425 residues and the shorter prefix 57. The tokenizer's special-token mask and attention mask were used together so the mean included residues only, excluding padding and boundary tokens. The resulting residue counts were exactly 425 and 57; the batch output had shape 2 x 320 and all values were finite. Repeating the full-length sequence alone produced zero maximum absolute difference in this one run. Embedding it alone versus alongside the short input differed by at most `6.556510925292969e-07`. This supports padding correctness for this example but is not a universal determinism guarantee. [Original ESM examples](https://github.com/facebookresearch/esm); [PyTorch inference mode](https://docs.pytorch.org/docs/stable/generated/torch.autograd.grad_mode.inference_mode.html).

The three forward passes used for this check took 4.273 seconds including initial GPU setup after loading, with reported peak allocated GPU memory 81.77 MiB. This is allocator-reported memory for the process, not total GPU memory use.

## Small batch measurements

Using 16 actual amylase sequences of length 425, no scores, one initial batch-1 warmup and one timed forward pass per size, with GPU synchronization around each forward pass:

| Batch size | Warmed forward time | Peak allocated GPU memory |
| ---: | ---: | ---: |
| 1 | 0.0051 s | 70.78 MiB |
| 4 | 0.0138 s | 102.07 MiB |
| 8 | 0.0235 s | 143.79 MiB |
| 16 | 0.0530 s | 229.81 MiB |

These figures omit tokenization, cache writing, loading and other pipeline costs. Each timing is one observation, and free hardware resources vary. They do not justify claiming an end-to-end runtime, optimal batch size or full-data capacity. All checked outputs were finite.

## Implementation plan

Varun approved this stage after the feasibility check. Implemented results and verification are recorded below.

1. Add a focused representation module, separate from dataset loading, selection, measurement accounting and the web catalog. Verify the installed APIs and pin a compatible model revision and software requirements; do not silently install or alter system packages. Load only the base model without the unused pooling layer.
2. Accept allowed sequences and stable identifiers without scores. Tokenize in batches and average only residue embeddings, excluding padding and special tokens. Use evaluation mode and inference mode. Reject invalid sequences, truncation or mismatched identifiers rather than producing ambiguous results. Make the selected device, precision, checkpoint revision and execution settings explicit.
3. Store numerical representations and metadata in a reproducible cache keyed by sequence identity and representation settings, including dataset and reference fingerprints, tokenizer/model revision and software versions. Use a non-pickle format, validate dimensions, finite values, IDs and fingerprints on read, and write without destroying an existing valid cache. Define behavior for an interrupted or partial write. Do not store measured scores.
4. Add meaningful tests for special-token and padding handling, repeated or duplicate IDs, mismatched cached settings, malformed sequences, finite 320-dimensional output, and a sequence embedded alone versus in an unequal-length batch. Separate lightweight tests from an explicitly invoked real-model/GPU check so ordinary tests do not require network or a GPU.
5. After checks pass, benchmark a small representative group and only then produce the amylase representation cache. Record model-file fingerprints, actual settings, elapsed time, peak memory, source data fingerprint and results. Do not claim that representations improve the model until a separately specified fair comparison is run.

The present isolated workaround is not yet a permanent application requirement or a chosen production fallback. Decide on a reproducible environment after comparing options; CPU and other Python installations remain untested. The ensemble, prediction intervals, detection and repair stay outside this implementation stage.

## Implementation and full amylase cache

The representation and cache modules are separate from the runner, catalog and selection methods. The real-model check passed using the same pinned checkpoint, CUDA device and process-local `TORCH_DISABLE_NATIVE_JIT=1`; the maximum padded/unpadded absolute difference was `6.556510925292969e-07`. Eleven ordinary unit tests passed without network access or a GPU, including cache corruption, duplicate identifiers, token loss, non-finite values and padding checks.

The explicitly invoked full cache run generated 3,706 vectors of 320 float32 values from all local amylase sequences, without storing scores. The embedding step took 19.2066 seconds and reported peak allocated GPU memory 238.23 MiB in this environment; timing excludes model loading and cache writing. The cache is `output/representations/amylase_esm2_c731040_v2.npz`, SHA-256 `d1092467446bb7cf48d6ae53d51207fb8acc89fa0d60bf59c31a831c6ecd73a3`. Its metadata records model-file hashes, source and reference hashes, code hashes, versions, pooling, precision, device and settings. Cache contents and source-ordered IDs were validated after writing.

Three individually recomputed vectors from an earlier otherwise-equivalent full run matched their batch outputs within `7.16e-07` maximum absolute difference. A second complete run using the final metadata produced numerically identical vectors to that earlier run in this environment. This is a limited reproducibility check, not a guarantee across devices, versions or future runs. Neither cache was used to train or evaluate a fitness predictor. The five unused pretraining-head weight warnings remain expected for the base model; no missing base pooling layer was loaded.
