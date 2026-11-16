"""Amylase source paths and FLIP2 measurement adapter."""
from pathlib import Path

from app.datasets.flip2 import load_flip2

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / 'data/raw/flip2/amylase/close_to_far.csv'
REFERENCE = ROOT / 'data/amylase_reference.fasta'


def load_amylase(data_path, reference_path, max_mutations):
    return load_flip2(data_path, reference_path, max_mutations)
