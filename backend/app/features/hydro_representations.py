"""Verify a score-free representation cache for one hydrophobic-core protein."""
import csv
import hashlib
import io
import json
from pathlib import Path

import numpy as np

from app.datasets.amylase import ROOT
from app.datasets.hydro import DATA, PROTEINS, REFERENCES
from app.features.representation_cache import load_cache
from app.features.representations import MODEL, REVISION, sequence_id

CACHE_HASHES = {'P06241': '0600442274c7be186dcc40f7a1e3fbbebae44b57466c36420084acddf152bbc7',
                'P01053': '64d019598ecf5fcfc428d434d099f76f6efeee6f9e18c37d6d1b35dbc1a75b6d',
                'P0A9X9': 'f474138824587bf3d37f9471eab43a0f1b11f593bf2c0eee1407814e6355dc34'}


def load_verified_representations(protein, data_path=DATA, reference_path=None):
    if protein not in PROTEINS:
        raise ValueError('Unknown hydrophobic-core protein')
    reference_path = REFERENCES[protein] if reference_path is None else Path(reference_path)
    path = ROOT / 'output/representations' / f'hydro_{protein}_esm2_c731040.npz'
    if hashlib.sha256(path.read_bytes()).hexdigest() != CACHE_HASHES[protein]:
        raise ValueError('Representation cache fingerprint mismatch')
    data, reference = Path(data_path).read_bytes(), reference_path.read_bytes()
    rows = csv.DictReader(io.StringIO(data.decode('utf-8'), newline=''))
    if 'sequence' not in (rows.fieldnames or []):
        raise ValueError('Missing sequence column')
    identifiers = [sequence_id(row['sequence']) for row in rows if len(row['sequence']) == PROTEINS[protein]]
    with np.load(path, allow_pickle=False) as archive:
        settings = json.loads(archive['metadata'].item())['settings']
    expected = {'dataset_sha256': hashlib.sha256(data).hexdigest(),
                'reference_sha256': hashlib.sha256(reference).hexdigest(),
                'model': MODEL, 'revision': REVISION,
                'pooling': 'residue_mean_excluding_padding_and_special_tokens', 'dtype': 'float32'}
    if any(settings.get(key) != value for key, value in expected.items()):
        raise ValueError('Representation settings do not match expected sources')
    return dict(zip(identifiers, load_cache(path, identifiers, settings)))
