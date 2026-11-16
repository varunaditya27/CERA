"""Construct finite, cost-ordered reward changes for development warnings."""
import copy

from app.reward_spec import LIMITS, validate_spec

TERMS = {'support_shift': 'distance_penalty', 'coverage': 'uncertainty_penalty',
         'disagreement': 'uncertainty_penalty', 'diversity': 'diversity_bonus'}
STEPS = (0.25, 0.5, 1.0)
TERM_COST = 0.05


def repair_candidates(spec, warning_type):
    validate_spec(spec)
    if warning_type not in TERMS:
        raise ValueError('Unsupported repair type')
    name = TERMS[warning_type]
    current = spec['terms'][name]['weight']
    low, high = LIMITS[name]
    candidates, seen = [], set()
    for step in STEPS:
        value = min(high, current + step)
        if value <= current or value in seen:
            continue
        seen.add(value)
        proposed = copy.deepcopy(spec)
        proposed['terms'][name]['weight'] = value
        validate_spec(proposed)
        candidates.append({'specification': proposed, 'term': name,
                           'cost': (value - current) / (high - low) + TERM_COST})
    return sorted(candidates, key=lambda candidate: (candidate['cost'], candidate['specification']['terms'][name]['weight']))
