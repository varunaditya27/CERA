# Dataset sources and attribution

The CSVs in `raw/flip2/` are extracted without modification from the FLIP2 benchmark's gzip files. The split files and benchmark documentation are available from [FLIP2](https://flip.protein.properties/) and the [FLIP2 Zenodo archive, version 3](https://zenodo.org/records/18433203). Cite Didi et al., *FLIP2: Expanding Protein Fitness Landscape Benchmarks for Real-World Machine Learning Applications*, ICML 2026, and the original experimental sources below when using the data. Consult the upstream dataset README files for attribution and licensing requirements.

## Alpha amylase

- Local split: `raw/flip2/amylase/close_to_far.csv`
- [FLIP2 split download](https://flip.protein.properties/assets/splits/amylase/close_to_far.csv.gz); [upstream dataset README](https://zenodo.org/api/records/18433203/files/amylase/README.md/content)
- [Original data: AMY_BACSU](https://github.com/florisvdf/mutation-predictability/tree/main/data/AMY_BACSU)
- Original publication: Van der Flier et al., “Enzyme structure correlates with variant effect predictability,” *Computational and Structural Biotechnology Journal*, volume 23, pp. 3489–3497 (2024).
- License identified by FLIP2: MIT.

## Imine reductase (IRED)

- Local split: `raw/flip2/ired/two_to_many.csv`
- [FLIP2 split download](https://flip.protein.properties/assets/splits/ired/two_to_many.csv.gz); [upstream dataset README](https://zenodo.org/api/records/18433203/files/ired/README.md/content)
- [Original data: Zenodo record 11357236](https://zenodo.org/records/11357236)
- Original publication: Gantz et al., “Microdroplet screening rapidly profiles a biocatalyst to enable its AI-assisted engineering,” [bioRxiv (2024)](https://doi.org/10.1101/2024.04.08.588565).
- License identified by FLIP2: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
- The benchmark website lists 17,143 variants, while this split has 8,586 rows; the reason remains to be investigated.

## Hydrophobic core

- Local split: `raw/flip2/hydro/low_to_high.csv`
- [FLIP2 split download](https://flip.protein.properties/assets/splits/hydro/low_to_high.csv.gz); [upstream dataset README](https://zenodo.org/api/records/18433203/files/hydro/README.md/content)
- Original data: Escobedo, Voigt, Faure and Lehner, *Files to replicate the figures in the manuscript “Genetics, energetics and allostery during a billion years of hydrophobic protein core evolution”* (2024), [Zenodo](https://doi.org/10.5281/zenodo.11175470).
- License identified by FLIP2: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

## GB1 (original FLIP)

- Local split: `raw/flip/gb1/low_vs_high.csv`; [benchmark download](https://flip.protein.properties/assets/splits/gb1/low_vs_high.csv.gz); [FLIP2 archive README](https://zenodo.org/api/records/18433203/files/gb1/README.md/content).
- Original experimental paper: Wu et al., [“Adaptation in protein fitness landscapes is facilitated by indirect paths”](https://doi.org/10.7554/eLife.16965), *eLife* (2016); [original data supplement](https://doi.org/10.7554/eLife.16965.024).
- [Original FLIP GB1 documentation](https://github.com/J-SNACKKB/FLIP/blob/main/splits/gb1/README.md) identifies four variable sites and explains that the full wild-type sequence was inferred from PDB 5LDE. It identifies the original data as CC BY 4.0 and modified FLIP split data as AFL-3; the FLIP2 archive README identifies CC BY 4.0. Review both upstream notices before redistribution.
- In `low_vs_high`, training variants fall below wild-type fitness and test variants are the remainder. The validation column uses blank values as well as `True`.

## ProteinGym GFP fluorescence assay

- Local file: `raw/proteingym/GFP_AEQVI_Sarkisyan_2016.csv`, extracted from the [ProteinGym v1.3 substitutions archive](https://marks.hms.harvard.edu/proteingym/ProteinGym_v1.3/DMS_ProteinGym_substitutions.zip). The full archive is not stored in this repository. `raw/proteingym/DMS_substitutions_reference.csv` retains the benchmark reference metadata and wild-type sequence.
- Original publication: Sarkisyan et al., [“Local fitness landscape of the green fluorescent protein”](https://doi.org/10.1038/nature17995), *Nature* (2016).
- [ProteinGym repository and citation](https://github.com/OATML-Markslab/ProteinGym); [reference file documentation](https://github.com/OATML-Markslab/ProteinGym/blob/main/reference_files/reference_files_description.md). ProteinGym states that higher `DMS_score` indicates higher fitness. Check the original data's terms before redistribution; the repository's MIT software license alone does not establish the assay data license.
