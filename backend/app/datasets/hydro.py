"""Hydrophobic-core dataset paths and separate per-protein measurement adapter."""
from app.datasets.amylase import ROOT
from app.datasets.flip2 import load_flip2

DATA = ROOT / 'data/raw/flip2/hydro/low_to_high.csv'
PROTEINS = {'P06241': 57, 'P01053': 63, 'P0A9X9': 65}
REFERENCES = {name: ROOT / 'data/hydro_references' / f'{name}.fasta' for name in PROTEINS}


def load_hydro(data_path, reference_path, max_mutations):
    return load_flip2(data_path, reference_path, max_mutations, set(PROTEINS.values()))
