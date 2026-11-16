"""Compare predictor rankings across pre-reveal candidate groups."""
import random

import numpy as np
from scipy.stats import rankdata

from app.experiments.predictor_group import predict_members


def group_correlations(values):
    values = np.asarray(values, dtype=float)
    if values.ndim != 2 or values.shape[0] != 5 or values.shape[1] < 2 or not np.isfinite(values).all():
        raise ValueError('Expected five finite predictor rows and at least two candidates')
    ranks = np.asarray([rankdata(row) for row in values])
    if any(np.ptp(row) == 0 for row in ranks):
        return None
    matrix = np.corrcoef(ranks)
    correlations = matrix[np.triu_indices(5, 1)]
    if not np.isfinite(correlations).all():
        return None
    return float(correlations.mean())


def compare_groups(seed, round_number, models, vectors, ranked, ranges):
    if len(ranked) < 100 or len(set(ranked)) != len(ranked) or set(ranked) != set(ranges):
        raise ValueError('Invalid historical candidate list')
    values = predict_members(models, vectors, ranked)
    means = np.asarray([ranges[i]['mean'] for i in ranked])
    spreads = np.asarray([ranges[i]['spread'] for i in ranked])
    if not (np.allclose(values.mean(axis=0), means, rtol=1e-10, atol=1e-12)
            and np.allclose(values.std(axis=0), spreads, rtol=1e-10, atol=1e-12)):
        raise ValueError('Historical candidate predictions mismatch')
    sample_seed = 4000 + 100 * seed + round_number
    middle = (len(ranked) - 100) // 2
    groups = {'top': list(range(100)), 'middle': list(range(middle, middle + 100)),
              'bottom': list(range(len(ranked) - 100, len(ranked))),
              'random': random.Random(sample_seed).sample(range(len(ranked)), 100),
              'full': list(range(len(ranked)))}
    rows = []
    for name, indices in groups.items():
        value = group_correlations(values[:, indices])
        rows.append({'seed': seed, 'round': round_number, 'group': name, 'count': len(indices),
                     'sample_seed': sample_seed if name == 'random' else '',
                     'status': 'available' if value is not None else 'unavailable', 'correlation': value})
    return rows
