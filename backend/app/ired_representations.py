"""Validate the pinned IRED representation cache against its source files."""
import csv
import hashlib
import io
import json
from pathlib import Path

import numpy as np

from app.ired import DATA, REFERENCE
from app.amylase import ROOT
from app.representation_cache import load_cache
from app.representations import MODEL, REVISION, sequence_id

CACHE = ROOT / 'output/representations/ired_esm2_c731040.npz'
CACHE_SHA256 = '417c6215b07275fc6149842f8f5e0706528eeb238d09300ed40def91144ae0df'


def load_verified_representations(cache_path=CACHE, data_path=DATA, reference_path=REFERENCE):
    path = Path(cache_path)
    if hashlib.sha256(path.read_bytes()).hexdigest() != CACHE_SHA256:
        raise ValueError('Representation cache fingerprint mismatch')
    data, reference = Path(data_path).read_bytes(), Path(reference_path).read_bytes()
    rows = csv.DictReader(io.StringIO(data.decode('utf-8'), newline=''))
    if 'sequence' not in (rows.fieldnames or []):
        raise ValueError('Missing sequence column')
    identifiers = [sequence_id(row['sequence']) for row in rows]
    with np.load(path, allow_pickle=False) as archive:
        settings = json.loads(archive['metadata'].item())['settings']
    expected = {'dataset_sha256': hashlib.sha256(data).hexdigest(),
                'reference_sha256': hashlib.sha256(reference).hexdigest(),
                'model': MODEL, 'revision': REVISION,
                'pooling': 'residue_mean_excluding_padding_and_special_tokens', 'dtype': 'float32'}
    if any(settings.get(key) != value for key, value in expected.items()):
        raise ValueError('Representation settings do not match expected sources')
    return dict(zip(identifiers, load_cache(path, identifiers, settings)))
