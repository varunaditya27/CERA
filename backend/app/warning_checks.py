"""Development warning rules; warnings do not diagnose causes."""
import itertools
import math

import numpy as np
from scipy.spatial.distance import cdist
from scipy.stats import spearmanr


def _result(kind, stage, status, identifiers, value=None, threshold=None, reason=None, evidence=None):
    return {'type': kind, 'stage': stage, 'status': status, 'identifiers': list(identifiers),
            'value': value, 'threshold': threshold, 'reason': reason, 'evidence': evidence}


def constraint_warning(identifiers, candidates, reference, remaining, batch_size=10, max_mutations=4):
    ids = list(identifiers)
    if not isinstance(reference, str) or not reference or remaining < 0 or batch_size < 1 or max_mutations < 0:
        raise ValueError('Invalid constraint inputs')
    if any(not isinstance(identifier, str) for identifier in ids):
        raise ValueError('Invalid candidate identifier')
    reasons = []
    if not ids:
        reasons.append('empty_batch')
    if len(ids) != len(set(ids)):
        reasons.append('duplicate')
    if len(ids) > remaining or len(ids) > batch_size:
        reasons.append('budget_or_batch_limit')
    for identifier in ids:
        if identifier not in candidates:
            reasons.append('unknown_or_already_revealed')
            continue
        sequence = candidates[identifier]
        if not isinstance(sequence, str) or len(sequence) != len(reference):
            raise ValueError('Sequence and reference lengths must match')
        if sum(a != b for a, b in zip(sequence, reference)) > max_mutations:
            reasons.append('mutation_limit')
    return _result('constraint', 'pre_reveal', 'triggered' if reasons else 'not_triggered', ids,
                   threshold=max_mutations, reason=','.join(sorted(set(reasons))) if reasons else None)


def distance_snapshot(known_ids, batch_ids, vectors):
    known, batch = list(known_ids), list(batch_ids)
    if (len(set(known)) != len(known) or not batch or len(set(batch)) != len(batch)
            or set(known) & set(batch)):
        raise ValueError('Invalid pre-reveal identifiers')
    batch_vectors = np.asarray([vectors[i] for i in batch], dtype=np.float64)
    if batch_vectors.ndim != 2 or not batch_vectors.shape[1] or not np.isfinite(batch_vectors).all():
        raise ValueError('Invalid representations')
    known_vectors = np.asarray([vectors[i] for i in known], dtype=np.float64)
    if known and (known_vectors.ndim != 2 or known_vectors.shape[1] != batch_vectors.shape[1]
                  or not np.isfinite(known_vectors).all()):
        raise ValueError('Invalid representations')
    if len(known) < 2:
        return {'known_ids': known, 'batch_ids': batch, 'threshold': None, 'distances': {}}
    pairwise = cdist(known_vectors, known_vectors, metric='euclidean')
    np.fill_diagonal(pairwise, np.inf)
    nearest_other = pairwise.min(axis=1)
    rank = math.ceil(0.9 * len(known))
    threshold = float(np.partition(nearest_other, rank - 1)[rank - 1])
    distances = cdist(batch_vectors, known_vectors, metric='euclidean').min(axis=1)
    return {'known_ids': known, 'batch_ids': batch, 'threshold': threshold,
            'distances': {identifier: float(distance) for identifier, distance in zip(batch, distances)}}


def support_warning(snapshot, ranges, measurements):
    batch = snapshot['batch_ids']
    if set(batch) != set(measurements) or not set(batch).issubset(ranges):
        raise ValueError('Measurements do not match pre-reveal batch')
    for identifier in batch:
        lower, upper, score = ranges[identifier]['lower'], ranges[identifier]['upper'], measurements[identifier]
        if not all(math.isfinite(x) for x in (lower, upper, score)) or lower > upper:
            raise ValueError('Invalid score or range')
    if snapshot['threshold'] is None:
        return _result('support_shift', 'post_reveal', 'unavailable', batch, reason='fewer_than_two_known')
    threshold = snapshot['threshold']
    if not math.isfinite(threshold) or threshold < 0 or set(batch) != set(snapshot['distances']):
        raise ValueError('Invalid pre-reveal distance snapshot')
    qualifying = []
    for identifier in batch:
        lower, upper, score = ranges[identifier]['lower'], ranges[identifier]['upper'], measurements[identifier]
        distance = snapshot['distances'][identifier]
        if not math.isfinite(distance) or distance < 0:
            raise ValueError('Invalid distance')
        if distance > threshold and not lower <= score <= upper:
            qualifying.append(identifier)
    return _result('support_shift', 'post_reveal', 'triggered' if len(qualifying) >= 3 else 'not_triggered',
                   batch, len(qualifying), 3, evidence={'distance_threshold': threshold, 'qualifying_ids': qualifying})


def coverage_warning(history):
    entries = list(history)
    if any(not isinstance(identifier, str) or not isinstance(covered, bool) for identifier, covered in entries):
        raise ValueError('Invalid coverage history')
    if len(entries) < 30:
        return _result('coverage', 'post_reveal', 'unavailable', [i for i, _ in entries],
                       threshold=0.75, reason='fewer_than_30_measurements')
    window = entries[-30:]
    count = sum(covered for _, covered in window)
    return _result('coverage', 'post_reveal', 'triggered' if count / 30 < 0.75 else 'not_triggered',
                   [i for i, _ in window], count / 30, 0.75, evidence={'covered': count, 'count': 30})


def disagreement_warning(means, members):
    if any(not isinstance(i, str) or not math.isfinite(v) for i, v in means.items()):
        raise ValueError('Invalid candidate predictions')
    top = sorted(means, key=lambda i: (-means[i], i))[:100]
    if set(members) != set(top):
        raise ValueError('Member predictions must match the top candidates')
    if not top:
        return _result('disagreement', 'pre_reveal', 'unavailable', top,
                       threshold=0.5, reason='fewer_than_two_candidates')
    matrix = np.asarray([members[i] for i in top], dtype=np.float64)
    if matrix.shape != (len(top), 5) or not np.isfinite(matrix).all():
        raise ValueError('Invalid member predictions')
    if len(top) < 2:
        return _result('disagreement', 'pre_reveal', 'unavailable', top,
                       threshold=0.5, reason='fewer_than_two_candidates', evidence={'members': members})
    if any(np.ptp(matrix[:, index]) == 0 for index in range(5)):
        return _result('disagreement', 'pre_reveal', 'unavailable', top,
                       threshold=0.5, reason='constant_member_ranking', evidence={'members': members})
    correlations = [float(spearmanr(matrix[:, a], matrix[:, b]).statistic)
                    for a, b in itertools.combinations(range(5), 2)]
    if not np.isfinite(correlations).all():
        return _result('disagreement', 'pre_reveal', 'unavailable', top,
                       threshold=0.5, reason='undefined_correlation', evidence={'members': members})
    value = sum(correlations) / len(correlations)
    return _result('disagreement', 'pre_reveal', 'triggered' if value < 0.5 else 'not_triggered',
                   top, value, 0.5, evidence={'members': members, 'pairwise_correlations': correlations})


def diversity_warning(batch):
    if not batch or any(not isinstance(i, str) or not isinstance(s, str) or not s for i, s in batch.items()):
        raise ValueError('Invalid batch sequences')
    ids = list(batch)
    sequences = list(batch.values())
    if len(set(map(len, sequences))) != 1 or len(set(sequences)) != len(sequences):
        raise ValueError('Batch sequences must be unique and have equal lengths')
    if len(ids) < 2:
        return _result('diversity', 'pre_reveal', 'unavailable', ids, threshold=2,
                       reason='fewer_than_two_sequences')
    distances = [sum(a != b for a, b in zip(left, right))
                 for left, right in itertools.combinations(sequences, 2)]
    value = sum(distances) / len(distances)
    return _result('diversity', 'pre_reveal', 'triggered' if value < 2 else 'not_triggered',
                   ids, value, 2, evidence={'pair_count': len(distances)})
