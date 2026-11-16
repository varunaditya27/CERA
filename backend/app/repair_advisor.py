"""Validate a model's preference for one member of a fixed repair menu."""
import json

from app.gemini_client import GeminiError
from app.goal_compiler import _unique_object


def advise_repair(request, warning_type, candidates):
    options = [{'option': i, 'term': candidate['term'],
                'weight': candidate['specification']['terms'][candidate['term']]['weight'],
                'cost': candidate['cost']} for i, candidate in enumerate(candidates)]
    attempts = []
    for _ in range(2):
        try:
            text, usage = request(warning_type, options)
            response = json.loads(text, object_pairs_hook=_unique_object)
            if (not isinstance(response, dict) or set(response) != {'option'}
                    or not isinstance(response['option'], int) or isinstance(response['option'], bool)
                    or not 0 <= response['option'] < len(options)):
                raise ValueError('Invalid repair choice')
        except GeminiError as error:
            attempts.append({'status': str(error)})
            if str(error) != 'invalid_response':
                break
        except (TypeError, ValueError):
            attempts.append({'status': 'invalid_choice'})
        else:
            attempts.append({'status': 'accepted', 'usage': usage})
            return {'source': 'gemini', 'option': response['option'], 'options': options, 'attempts': attempts}
    return {'source': 'fallback', 'option': 0, 'options': options, 'attempts': attempts}
