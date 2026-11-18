# Preparing the imine reductase dataset

Completed 16 November 2026. This step prepares a second protein for later evaluation; it does not report an IRED search result or resolve every source-provenance question.

An imine reductase is an enzyme. The local dataset contains variants of the *Streptosporangium roseum* enzyme and measurements derived from a microfluidic screen. The original [laboratory archive](https://zenodo.org/records/14544486) describes its fitness values as logarithmic enrichment relative to the original enzyme. The [FLIP2 benchmark](https://flip.protein.properties/) uses a split that moves from variants with at most two substitutions to those with more.

## Source checks

Fetched the laboratory's [active-data table at commit 6a9e87c6](https://github.com/Hollfelder-Lab/lrDMS-IRED/blob/6a9e87c6c788e77d67e9e7ccad1208f1f60f859c/data/srired_active_data.csv). Its SHA-256 was `81964bd5f366310627641ddaba573d77242803969570aa383d9f3912364adc0b`, matching the earlier evidence ledger. Exactly one row has `WT=True`. Its 290-residue amino-acid sequence, with the terminal stop marker removed, is saved as [ired_reference.fasta](../data/ired_reference.fasta), SHA-256 `57b552947108c2ec32a57305bfc41b64555425b32421aea13d7d9df9e365122d`.

All 8,586 local sequence/target pairs matched a sequence and fitness in the pinned laboratory table within 1e-8. Every local train variant has at most two changes relative to this reference; every local test variant has more than two. The development cap of four changes leaves 4,408 train and 3,225 test variants eligible; 953 test variants exceed it. The local split's SHA-256 is `55425e46a5be5b50fb79dbf8be677422355969da065241e11325a61348e19fae`.

The original laboratory's pinned [data README](https://github.com/Hollfelder-Lab/lrDMS-IRED/blob/6a9e87c6c788e77d67e9e7ccad1208f1f60f859c/data/README.md) describes approximately 11,000 sequences with a determinable fitness in its active table, and approximately 6,000 with no measured activity in a separate inactive table. Since all local sequence/target pairs were matched to the active table, the local benchmark is a subset of reported measured-fitness examples. This supports an important selection limitation: it is not a complete representation of all screened variants. It does not reveal the exact rules used to select the 8,586 benchmark rows or prove why each inactive variant is absent.

The FLIP2 authors' [manuscript, Table 1](https://flip.protein.properties/assets/FLIP_manuscipt.pdf) lists 3,746 training, 662 validation and 4,178 test examples for the IRED two-to-many split. A fresh count of the local file matches these three counts exactly: the 662 validation examples are marked `set=train, validation=True`. The three published split counts total 8,586, despite the same table listing 17,143 as the overall dataset count. This is evidence that the local row count agrees with the published split table, not an explanation of the filtering or proof that every row is identical to the authors' source snapshot. The linked manuscript was accessed on 16 November 2026 and may be revised later.

The benchmark describes a larger screened set of 17,143 variants, whereas this downloaded split has 8,586. The matching exercise does not reconstruct the exact benchmark filtering or treatment of inactive variants. Those remain open source questions, and results must describe the local split rather than the full screened collection. The lab and benchmark sources have their own attribution and license terms; see [dataset sources](../data/SOURCES.md).

### Source recheck on 18 November 2026

The current [FLIP2 IRED split download](https://flip.protein.properties/assets/splits/ired/two_to_many.csv.gz) decompresses byte for byte to the local CSV. Its decompressed SHA-256 is `55425e46a5be5b50fb79dbf8be677422355969da065241e11325a61348e19fae`; the downloaded compressed file's SHA-256 is `aa45a2f85fb1af87b6b0e86397b3f8f292a061dc574be2536673b5bd490b0e74`. This confirms agreement with the published split on that date, not why it has fewer rows than the website's overall count. The [benchmark repository's current loading example](https://github.com/J-SNACKKB/FLIP/tree/e74069fe09490c6a44a8d7ff8c2811b61f24ec82#quick-start) excludes rows marked for validation from official training. CERA's low-change-start study instead explicitly sampled eligible train-side rows including validation-marked rows, as documented in its [study plan](ired_low_change_study_plan.md); its results are therefore not an official train/validation/test benchmark comparison. No past results have been changed or reclassified as independent validation.

## Representation and runner checks

The pinned ESM-2 model produced a score-free cache of 8,586 vectors, each with 320 numbers. The cache SHA-256 is `417c6215b07275fc6149842f8f5e0706528eeb238d09300ed40def91144ae0df`. It contains sequence identifiers, vectors and metadata, not fitness values. GPU generation took about 20.95 seconds in this environment, with a reported peak allocated memory of about 180 MiB; these are observations, not portable performance claims. A separate GPU pass regenerated three vectors with maximum absolute difference zero in the same environment. The model loader reported unused language-model-head weights, as in the earlier amylase check.

The cache loader verifies its file fingerprint, sequence order, source and reference fingerprints, model revision, pooling and finite vectors. The measurement runner accepted the verified IRED files and enforced the existing 100-initial/100-new budget in a structural check. A separate synthetic-data test exercised the dataset dispatch through one complete prediction-and-reveal round without using IRED outcomes. The full backend suite passed 58 tests. These checks do not establish predictive performance.

To regenerate a cache at a new path, after installing the embedding requirements and reviewing device compatibility:

```sh
TORCH_DISABLE_NATIVE_JIT=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend python3 scripts/embed_amylase.py --dataset ired --device cuda --batch-size 16 --output output/representations/my-ired-cache.npz
```

The pilot accepts `--dataset ired`, but its current cache fingerprint is pinned to the checked file. A newly generated cache needs review before that pin is updated. No IRED reward or repair evaluation was run in this step. Freeze development choices and a matched evaluation procedure before using this dataset to judge them.
