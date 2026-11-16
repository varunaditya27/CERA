"""Calculate pre-reveal candidate distances relative to known representations."""
import numpy as np
from scipy.spatial.distance import cdist


def normalized_distances(known_ids, candidate_ids, vectors):
    known, candidates = list(known_ids), list(candidate_ids)
    if (len(known) < 2 or not candidates or len(set(known)) != len(known)
            or len(set(candidates)) != len(candidates) or set(known) & set(candidates)):
        raise ValueError('Invalid distance identifiers')
    known_vectors = np.asarray([vectors[i] for i in known], dtype=np.float64)
    candidate_vectors = np.asarray([vectors[i] for i in candidates], dtype=np.float64)
    if (known_vectors.ndim != 2 or candidate_vectors.ndim != 2 or not known_vectors.shape[1]
            or known_vectors.shape[1] != candidate_vectors.shape[1]
            or not np.isfinite(known_vectors).all() or not np.isfinite(candidate_vectors).all()):
        raise ValueError('Invalid distance representations')
    pairwise = cdist(known_vectors, known_vectors, metric='euclidean')
    np.fill_diagonal(pairwise, np.inf)
    scale = float(pairwise.min(axis=1).max())
    if not np.isfinite(scale) or scale <= 0:
        raise ValueError('Cannot normalize distances from degenerate known representations')
    raw = cdist(candidate_vectors, known_vectors, metric='euclidean').min(axis=1)
    if not np.isfinite(raw).all():
        raise ValueError('Invalid candidate distances')
    return {'scale': scale, 'distances': {i: float(min(distance / scale, 1.0))
                                           for i, distance in zip(candidates, raw)}}


def known_distances(known_ids, vectors):
    known = list(known_ids)
    if len(known) < 2 or len(set(known)) != len(known):
        raise ValueError('Invalid known identifiers')
    values = np.asarray([vectors[i] for i in known], dtype=np.float64)
    if values.ndim != 2 or not values.shape[1] or not np.isfinite(values).all():
        raise ValueError('Invalid distance representations')
    pairwise = cdist(values, values, metric='euclidean')
    np.fill_diagonal(pairwise, np.inf)
    distances = pairwise.min(axis=1)
    scale = float(distances.max())
    if not np.isfinite(scale) or scale <= 0:
        raise ValueError('Cannot normalize distances from degenerate known representations')
    return {identifier: float(distance / scale) for identifier, distance in zip(known, distances)}
