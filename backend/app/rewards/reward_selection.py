"""Select a constrained batch using a validated reward specification."""
import math

import numpy as np

from app.rewards.reward_spec import validate_spec

ALPHABET = set('ACDEFGHIKLMNPQRSTVWY')


def select_batch(spec, candidates, reference, remaining):
    validate_spec(spec)
    if (not isinstance(reference, str) or not reference or set(reference) - ALPHABET
            or not isinstance(remaining, int) or isinstance(remaining, bool) or remaining < 0
            or not isinstance(candidates, dict)):
        raise ValueError('Invalid selection inputs')
    eligible, seen = {}, set()
    for identifier, candidate in candidates.items():
        if (not isinstance(identifier, str) or not identifier or not isinstance(candidate, dict)
                or set(candidate) != {'sequence', 'mean', 'spread', 'distance'}):
            raise ValueError('Invalid candidate')
        sequence = candidate['sequence']
        if (not isinstance(sequence, str) or len(sequence) != len(reference)
                or set(sequence) - ALPHABET or sequence in seen):
            raise ValueError('Invalid candidate sequence')
        seen.add(sequence)
        values = [candidate[key] for key in ('mean', 'spread', 'distance')]
        if (any(isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x) for x in values)
                or candidate['spread'] < 0 or not 0 <= candidate['distance'] <= 1):
            raise ValueError('Invalid candidate features')
        if sum(a != b for a, b in zip(sequence, reference)) <= spec['hard_constraints']['max_mutations']:
            eligible[identifier] = candidate
    terms = spec['terms']
    chosen = []
    count = min(remaining, spec['budget']['batch_size'], len(eligible))
    if not count:
        return chosen
    ids = sorted(eligible)
    rows = [eligible[i] for i in ids]
    sequences = np.asarray([list(row['sequence'].encode('ascii')) for row in rows], dtype=np.uint8)
    means = np.asarray([row['mean'] for row in rows], dtype=np.float64)
    spreads = np.asarray([row['spread'] for row in rows], dtype=np.float64)
    distances = np.asarray([row['distance'] for row in rows], dtype=np.float64)
    with np.errstate(over='ignore', invalid='ignore'):
        base = means - terms['uncertainty_penalty']['weight'] * spreads - terms['distance_penalty']['weight'] * distances
    diversity = np.zeros(len(ids), dtype=np.float64)
    selected = np.zeros(len(ids), dtype=bool)
    while len(chosen) < count:
        with np.errstate(over='ignore', invalid='ignore'):
            scores = base + terms['diversity_bonus']['weight'] * diversity
        if not np.isfinite(scores[~selected]).all():
            raise ValueError('Non-finite reward')
        scores[selected] = -np.inf
        index = int(np.argmax(scores))
        chosen.append({'id': ids[index], 'reward': float(scores[index]), 'diversity': float(diversity[index])})
        selected[index] = True
        new_distance = np.count_nonzero(sequences != sequences[index], axis=1) / len(reference)
        diversity = new_distance if len(chosen) == 1 else np.minimum(diversity, new_distance)
    return chosen
