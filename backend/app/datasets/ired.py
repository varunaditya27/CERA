"""Pinned local IRED dataset and original laboratory reference."""
from app.datasets.amylase import ROOT

DATA = ROOT / 'data/raw/flip2/ired/two_to_many.csv'
REFERENCE = ROOT / 'data/ired_reference.fasta'
