"""Interpret a user goal within the existing fixed fitness-search constraints."""
import copy
import json

from app.llm.gemini_client import GeminiError
from app.llm.goal_compiler import DEFAULT_SPEC, _unique_object
from app.rewards.reward_spec import LIMITS, validate_spec


def compile_natural_goal(goal, request):
    if not isinstance(goal, str) or not goal.strip() or len(goal) > 1000:
        raise ValueError('Goal must contain 1–1000 characters')
    attempts = []
    for _ in range(2):
        usage = None
        try:
            text, usage = request(goal)
            proposal = json.loads(text, object_pairs_hook=_unique_object)
            if (not isinstance(proposal, dict) or set(proposal) != {'supported', *LIMITS}
                    or not isinstance(proposal['supported'], bool)):
                raise ValueError('Invalid goal response')
            if not proposal['supported']:
                raise UnsupportedGoal('Goal cannot be represented by the supported fitness search')
            spec = copy.deepcopy(DEFAULT_SPEC)
            for name in LIMITS:
                spec['terms'][name]['weight'] = proposal[name]
            validate_spec(spec)
        except UnsupportedGoal:
            raise
        except GeminiError as error:
            if str(error) != 'invalid_response':
                raise
            attempts.append({'status': 'invalid_response', **({'usage': error.usage} if error.usage is not None else {})})
        except (TypeError, ValueError, json.JSONDecodeError):
            attempts.append({'status': 'invalid_goal_response', **({'usage': usage} if isinstance(usage, dict) else {})})
        else:
            attempts.append({'status': 'accepted', 'usage': usage})
            return {'source': 'gemini', 'attempts': attempts, 'specification': spec, 'input_goal': goal}
    raise ValueError('Could not compile the goal from valid responses')


class UnsupportedGoal(ValueError):
    pass
