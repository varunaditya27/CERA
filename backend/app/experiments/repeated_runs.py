"""Run one predeclared method with a matched initial seed and bounded budget."""
import copy

from app.experiments.prediction_pilot import run_pilot
from app.experiments.random_baseline import run_random

METHODS = ('random', 'greedy', 'fixed', 'repair', 'gemini_repair', 'ucb', 'ei', 'genetic', 'adalead')


def run_one(path, seed, method, specification, advisor=None, model=None):
    if method not in METHODS:
        raise ValueError('Unknown comparison method')
    if method == 'random':
        return run_random(path, seed)
    options = {'seed': seed, 'role_seed': 2000 + seed, 'member_seed': 3000 + seed}
    if method in ('fixed', 'repair', 'gemini_repair'):
        options.update(reward_spec=copy.deepcopy(specification),
                       reward_origin={'source': 'repeated_matched_development'},
                       repair=method != 'fixed')
        if method == 'gemini_repair':
            if advisor is None:
                raise ValueError('Gemini repair requires an advisor with explicit fallback')
            options.update(repair_advisor=advisor, repair_model=model)
    elif method in ('ucb', 'ei'):
        options['acquisition'] = method
    elif method in ('genetic', 'adalead'):
        options['local_search'] = method
    return run_pilot(path, **options)
