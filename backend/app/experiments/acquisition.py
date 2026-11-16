"""Rank finite candidates with two uncertainty-guided acquisition rules."""
import math

import numpy as np
from scipy.special import ndtr


def acquisition_scores(ranges, best, method):
    if method not in ('ucb', 'ei') or not isinstance(best, (int, float)) or isinstance(best, bool) or not math.isfinite(best):
        raise ValueError('Invalid acquisition method or best score')
    scores = {}
    for identifier, prediction in ranges.items():
        if not isinstance(identifier, str) or not identifier:
            raise ValueError('Invalid candidate identifier')
        mean, spread = prediction['mean'], prediction['spread']
        if (any(isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x)
                for x in (mean, spread)) or spread < 0):
            raise ValueError('Invalid acquisition inputs')
        improvement = mean - best
        if not math.isfinite(improvement):
            raise ValueError('Invalid improvement')
        if method == 'ucb':
            score = mean + spread
        elif spread == 0:
            score = max(improvement, 0.0)
        else:
            with np.errstate(over='ignore', under='ignore'):
                z = improvement / spread
                score = improvement * ndtr(z) + spread * np.exp(-0.5 * z * z) / np.sqrt(2 * np.pi)
            score = max(float(score), 0.0)
        if not math.isfinite(score):
            raise ValueError('Non-finite acquisition score')
        scores[identifier] = float(score)
    return scores


def choose_acquisition(scores, count):
    if not isinstance(count, int) or isinstance(count, bool) or count < 0 or count > len(scores):
        raise ValueError('Invalid selection count')
    if any(not isinstance(i, str) or not i or not math.isfinite(v) for i, v in scores.items()):
        raise ValueError('Invalid acquisition scores')
    return sorted(scores, key=lambda identifier: (-scores[identifier], identifier))[:count]
