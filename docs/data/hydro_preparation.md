<div align="center">

# Preparing the three hydrophobic-core datasets

Dataset preparation

</div>

Completed 16 November 2026. This is dataset preparation, not a search-performance evaluation. The three groups are kept separate because they have different reference sequences and may have different measurement scales.

## What was checked

The [FLIP2 benchmark](https://flip.protein.properties/) describes variants of three protein domains whose seven core positions were varied. A protein's hydrophobic core is the water-avoiding interior that helps it fold; the measured score is a proxy from the authors' experiment, not a direct proof of real-world performance. The original study is [Escobedo et al.](https://pubmed.ncbi.nlm.nih.gov/40705891/).

Downloaded the original authors' [processed core-mutagenesis table](https://ftp.ncbi.nlm.nih.gov/geo/series/GSE266nnn/GSE266299/suppl/GSE266299_sparse_DTS_core_mutagenesis_scores.csv.gz). Its compressed SHA-256 is `4cd224d56a0004be70f1b33f055cb2a0d2846065497c94e4fcb8bb289a167b84`; its uncompressed CSV SHA-256 is `f258588a62a9616b93aff55efa2f869bc97587e4e547cb926b3bf37c0c0580ec`. Every one of the 24,935 local sequences matched exactly one source row, and every local target matched that row's `fitness_raw` value as a parsed floating-point number. The source also supplies `fitness_scaled`; the local target is **not** that column. In the checked rows, raw and scaled values are related by a positive linear transformation within each protein, but the local searches retain the raw scores and do not mix them across proteins. The [GEO record](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE266299) describes the experiment and its supplementary fields.

UniProt reference segments P06241 residues 85–141, P01053 residues 22–84 and P0A9X9 residues 5–69 were fetched and saved under [hydro_references](../../data/hydro_references). For every source row, the number of sequence changes from its corresponding segment matched the source's `Nham_aa` field. This independently supports the three mappings. The source's `WT` marker appears on one P01053 row only; it should not be treated as direct confirmation of a marked reference row for the other two proteins.

| Protein | Length | Local rows | Eligible train | Eligible test | Cached vectors |
| --- | ---: | ---: | ---: | ---: | ---: |
| P06241 | 57 | 9,972 | 263 | 747 | 9,972 |
| P01053 | 63 | 6,463 | 713 | 579 | 6,463 |
| P0A9X9 | 65 | 8,500 | 701 | 2,215 | 8,500 |

Eligibility here means no more than four substitutions from the matching reference. The benchmark's low-to-high split is based on scores across the combined file. Drawing initial observations from the train side therefore uses **privileged score-derived membership** to create the starting set, even though the selector is not given split labels or unseen scores. This limitation must be disclosed in any experiment. We have not established that these reference segments exhaust all experimental construct details or independently reconstructed every preprocessing step.

## Caches and checks

Each protein has its own score-free, 320-number-per-sequence cache under `output/representations/`. The cache SHA-256 values are:

- P06241: `0600442274c7be186dcc40f7a1e3fbbebae44b57466c36420084acddf152bbc7`
- P01053: `64d019598ecf5fcfc428d434d099f76f6efeee6f9e18c37d6d1b35dbc1a75b6d`
- P0A9X9: `f474138824587bf3d37f9471eab43a0f1b11f593bf2c0eee1407814e6355dc34`

The loader checks the cache and source fingerprints, matching reference, model revision, sequence order, shape and finite values. One vector from each group was independently regenerated together in a padded GPU batch; maximum absolute differences from the caches were approximately `1.67e-6`, `5.14e-7` and `9.54e-7` respectively. These are checks in the same software and hardware environment, not evidence of predictive accuracy.

The common FLIP2 loader validates rows and filters by the selected reference length before applying the mutation limit. The restricted measurement interface was checked for each real group; a synthetic one-round run checked experiment dispatch without using these groups' outcomes for tuning. All 74 backend tests passed. No hydrophobic-core search comparison was run in this preparation step.

For cache regeneration at a new path, replace `P06241` with the desired protein:

```sh
TORCH_DISABLE_NATIVE_JIT=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=backend:. python3 -m scripts.data.embed_amylase --dataset hydro-P06241 --device cuda --batch-size 32 --output output/representations/my-hydro-cache.npz
```

The pilot accepts `--dataset hydro-P06241`, `hydro-P01053` or `hydro-P0A9X9`. Its current cache fingerprints are pinned to the checked files; regenerated files need review before those pins change. Freeze the comparison procedure and development decisions before interpreting these evaluation datasets.
