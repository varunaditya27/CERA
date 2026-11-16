"""Select a constrained batch using a validated reward specification."""
import math

from app.reward_spec import validate_spec

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
    while len(chosen) < count:
        scored = []
        for identifier, candidate in eligible.items():
            if any(identifier == entry['id'] for entry in chosen):
                continue
            diversity = min((sum(a != b for a, b in zip(candidate['sequence'], eligible[entry['id']]['sequence']))
                             / len(reference) for entry in chosen), default=0.0)
            score = (candidate['mean'] - terms['uncertainty_penalty']['weight'] * candidate['spread']
                     - terms['distance_penalty']['weight'] * candidate['distance']
                     + terms['diversity_bonus']['weight'] * diversity)
            if not math.isfinite(score):
                raise ValueError('Non-finite reward')
            scored.append((score, identifier, diversity))
        score, identifier, diversity = min(scored, key=lambda row: (-row[0], row[1]))
        chosen.append({'id': identifier, 'reward': score, 'diversity': diversity})
    return chosen
