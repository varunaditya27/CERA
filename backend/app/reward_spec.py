"""Validate the finite set of reward options used in development."""
import math

LIMITS = {'uncertainty_penalty': (0.0, 2.0), 'distance_penalty': (0.0, 2.0),
          'diversity_bonus': (0.0, 1.0)}


def _keys(value, expected):
    if not isinstance(value, dict) or set(value) != set(expected):
        raise ValueError('Unexpected or missing specification fields')


def _integer(value, low, high):
    return isinstance(value, int) and not isinstance(value, bool) and low <= value <= high


def validate_spec(spec):
    _keys(spec, ('goal', 'terms', 'hard_constraints', 'budget', 'abstain_after_failed_repairs'))
    if spec['goal'] != 'maximize_fitness':
        raise ValueError('Unsupported goal')
    _keys(spec['terms'], LIMITS)
    for name, bounds in LIMITS.items():
        term = spec['terms'][name]
        _keys(term, ('weight', 'allowed_range'))
        limits = term['allowed_range']
        if (not isinstance(limits, list) or len(limits) != 2
                or any(isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x)
                       for x in limits)
                or tuple(limits) != bounds):
            raise ValueError('Invalid allowed range')
        weight = term['weight']
        if (isinstance(weight, bool) or not isinstance(weight, (int, float))
                or not math.isfinite(weight) or not bounds[0] <= weight <= bounds[1]):
            raise ValueError('Invalid reward weight')
    constraints, budget = spec['hard_constraints'], spec['budget']
    _keys(constraints, ('max_mutations',))
    _keys(budget, ('rounds', 'batch_size'))
    if (not _integer(constraints['max_mutations'], 0, 4)
            or not _integer(budget['rounds'], 1, 10)
            or not _integer(budget['batch_size'], 1, 10)
            or not _integer(spec['abstain_after_failed_repairs'], 1, 2)):
        raise ValueError('Specification exceeds development limits')
