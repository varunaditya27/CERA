"""Write and validate score-free sequence representation caches."""
import hashlib
import json
import os
import tempfile
from pathlib import Path

import numpy as np

from app.features.representations import FEATURES


def _validate(ids, vectors):
    if (ids.ndim != 1 or ids.dtype.kind != 'U' or not len(ids) or
            len(set(ids.tolist())) != len(ids) or
            any(len(value) != 64 or any(c not in '0123456789abcdef' for c in value) for value in ids.tolist())):
        raise ValueError('Invalid or duplicate sequence identifiers')
    if vectors.dtype != np.float32 or vectors.shape != (len(ids), FEATURES) or not np.isfinite(vectors).all():
        raise ValueError('Invalid representation array')


def _fingerprint(ids, vectors):
    digest = hashlib.sha256()
    digest.update('\n'.join(ids.tolist()).encode('ascii'))
    digest.update(vectors.astype('<f4', copy=False).tobytes(order='C'))
    return digest.hexdigest()


def save_cache(path, ids, vectors, settings, observations=None):
    path = Path(path)
    identifiers = np.asarray(ids)
    values = np.asarray(vectors)
    _validate(identifiers, values)
    metadata = {'settings': settings, 'observations': observations, 'content_sha256': _fingerprint(identifiers, values)}
    encoded = json.dumps(metadata, sort_keys=True, allow_nan=False)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix='.representations-', delete=False) as file:
            temporary = Path(file.name)
            np.savez_compressed(file, identifiers=identifiers, vectors=values, metadata=np.array(encoded))
            file.flush()
            os.fsync(file.fileno())
        os.link(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def load_cache(path, expected_ids, expected_settings):
    with np.load(path, allow_pickle=False) as archive:
        if set(archive.files) != {'identifiers', 'vectors', 'metadata'}:
            raise ValueError('Unexpected cache contents')
        ids, vectors = archive['identifiers'], archive['vectors']
        metadata = json.loads(archive['metadata'].item())
    _validate(ids, vectors)
    if (ids.tolist() != list(expected_ids) or metadata.get('settings') != expected_settings or
            metadata.get('content_sha256') != _fingerprint(ids, vectors)):
        raise ValueError('Cache metadata or content does not match')
    return vectors
