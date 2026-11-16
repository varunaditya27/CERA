"""Compile the supported fitness goal using checked model-proposed weights."""
import copy
import json

from app.gemini_client import GeminiError
from app.reward_spec import LIMITS, validate_spec

DEFAULT_SPEC = {'goal': 'maximize_fitness', 'terms': {
    'uncertainty_penalty': {'weight': 0.5, 'allowed_range': [0.0, 2.0]},
    'distance_penalty': {'weight': 0.3, 'allowed_range': [0.0, 2.0]},
    'diversity_bonus': {'weight': 0.1, 'allowed_range': [0.0, 1.0]}},
    'hard_constraints': {'max_mutations': 4}, 'budget': {'rounds': 10, 'batch_size': 10},
    'abstain_after_failed_repairs': 2}


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON key')
        result[key] = value
    return result


def compile_goal(request):
    attempts = []
    for _ in range(2):
        try:
            text, usage = request()
            weights = json.loads(text, object_pairs_hook=_unique_object)
            if not isinstance(weights, dict) or set(weights) != set(LIMITS):
                raise ValueError('Unexpected weights')
            spec = copy.deepcopy(DEFAULT_SPEC)
            for name, value in weights.items():
                spec['terms'][name]['weight'] = value
            validate_spec(spec)
        except GeminiError as error:
            attempts.append({'status': str(error)})
            if str(error) != 'invalid_response':
                break
        except (TypeError, ValueError, json.JSONDecodeError):
            attempts.append({'status': 'invalid_weights'})
        else:
            attempts.append({'status': 'accepted', 'usage': usage})
            return {'source': 'gemini', 'attempts': attempts, 'specification': spec}
    return {'source': 'fallback', 'attempts': attempts, 'specification': copy.deepcopy(DEFAULT_SPEC)}
