"""Check a reward change against recorded pre-reveal and revealed evidence."""
import math

import numpy as np
from scipy.stats import spearmanr

from app.repair_menu import TERMS, repair_candidates
from app.reward_selection import select_batch
from app.reward_spec import validate_spec


def _score(spec, row):
    terms = spec['terms']
    return (row['mean'] - terms['uncertainty_penalty']['weight'] * row['spread']
            - terms['distance_penalty']['weight'] * row['distance'])


def verify_repair(old, proposed, warning_type, candidates, reference, remaining,
                  counterexamples, calibration, earlier):
    validate_spec(old)
    validate_spec(proposed)
    if warning_type not in TERMS:
        raise ValueError('Unsupported warning type')
    unchanged = any(candidate['specification'] == proposed for candidate in repair_candidates(old, warning_type))
    original = select_batch(old, candidates, reference, remaining)
    counterexamples = list(counterexamples)
    if (not counterexamples or len(counterexamples) != len(set(counterexamples))
            or not set(counterexamples).issubset({item['id'] for item in original})):
        raise ValueError('Counterexamples must be selected by the recorded old rule')
    replay = select_batch(proposed, candidates, reference, remaining)
    displaced = not set(counterexamples).intersection(item['id'] for item in replay)
    for row in calibration:
        if set(row) != {'lower', 'upper', 'score'} or any(
                isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in row.values()
        ) or row['lower'] > row['upper']:
            raise ValueError('Invalid calibration evidence')
    for row in earlier:
        if set(row) != {'mean', 'spread', 'distance', 'score'} or any(
                isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in row.values()
        ) or row['spread'] < 0 or not 0 <= row['distance'] <= 1:
            raise ValueError('Invalid ranking evidence')
    coverage = (sum(row['lower'] <= row['score'] <= row['upper'] for row in calibration) / len(calibration)
                if len(calibration) >= 20 else None)
    old_rank = new_rank = None
    if len(earlier) >= 5:
        labels = np.asarray([row['score'] for row in earlier])
        old_values = np.asarray([_score(old, row) for row in earlier])
        new_values = np.asarray([_score(proposed, row) for row in earlier])
        if np.ptp(labels) and np.ptp(old_values) and np.ptp(new_values):
            old_rank = float(spearmanr(labels, old_values).statistic)
            new_rank = float(spearmanr(labels, new_values).statistic)
            if not math.isfinite(old_rank) or not math.isfinite(new_rank):
                old_rank = new_rank = None
    checks = {'allowed_change_and_constraints': unchanged, 'counterexamples_displaced': displaced,
              'calibration_coverage': None if coverage is None else 0.8 <= coverage <= 1.0,
              'earlier_rank_preserved': None if old_rank is None else new_rank >= old_rank - 0.05}
    return {'accepted': all(value is True for value in checks.values()), 'checks': checks,
            'coverage': coverage, 'old_rank': old_rank, 'new_rank': new_rank,
            'replayed_ids': [item['id'] for item in replay]}
