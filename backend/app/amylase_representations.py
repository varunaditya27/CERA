"""Validate the pinned amylase representation cache against source data."""
import csv
import hashlib
import io
import json
from pathlib import Path

import numpy as np

from app.amylase import DATA, REFERENCE, ROOT
from app.representation_cache import load_cache
from app.representations import MODEL, REVISION, sequence_id

CACHE = ROOT / 'output/representations/amylase_esm2_c731040_v2.npz'
CACHE_SHA256 = 'd1092467446bb7cf48d6ae53d51207fb8acc89fa0d60bf59c31a831c6ecd73a3'


def load_verified_representations(cache_path=CACHE, data_path=DATA, reference_path=REFERENCE):
    path = Path(cache_path)
    if hashlib.sha256(path.read_bytes()).hexdigest() != CACHE_SHA256:
        raise ValueError('Representation cache fingerprint mismatch')
    data = Path(data_path).read_bytes()
    reference = Path(reference_path).read_bytes()
    rows = csv.DictReader(io.StringIO(data.decode('utf-8'), newline=''))
    if 'sequence' not in (rows.fieldnames or []):
        raise ValueError('Missing sequence column')
    identifiers = [sequence_id(row['sequence']) for row in rows]
    with np.load(path, allow_pickle=False) as archive:
        metadata = json.loads(archive['metadata'].item())
    settings = metadata['settings']
    expected = {'dataset_sha256': hashlib.sha256(data).hexdigest(),
                'reference_sha256': hashlib.sha256(reference).hexdigest(),
                'model': MODEL, 'revision': REVISION,
                'pooling': 'residue_mean_excluding_padding_and_special_tokens', 'dtype': 'float32'}
    if any(settings.get(key) != value for key, value in expected.items()):
        raise ValueError('Representation settings do not match expected sources')
    vectors = load_cache(path, identifiers, settings)
    return dict(zip(identifiers, vectors))
