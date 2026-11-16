"""Send a fixed, score-free reward-weight request to Gemini."""
import json
import re
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

PROMPT = ('Choose nonnegative weights for a protein fitness search that maximizes predicted fitness. '
          'The uncertainty and distance penalties discourage uncertain or unfamiliar candidates; '
          'the diversity bonus encourages differences within a batch. Return only the three weights.')
SCHEMA = {'type': 'object', 'properties': {
    'uncertainty_penalty': {'type': 'number', 'minimum': 0, 'maximum': 2},
    'distance_penalty': {'type': 'number', 'minimum': 0, 'maximum': 2},
    'diversity_bonus': {'type': 'number', 'minimum': 0, 'maximum': 1}},
    'required': ['uncertainty_penalty', 'distance_penalty', 'diversity_bonus'],
    'additionalProperties': False}


class GeminiError(Exception):
    pass


def _request_json(api_key, model, prompt, schema):
    if not isinstance(api_key, str) or not api_key or not isinstance(model, str) or not re.fullmatch(r'[A-Za-z0-9._-]+', model):
        raise GeminiError('invalid_configuration')
    body = {'contents': [{'parts': [{'text': prompt}]}],
            'generationConfig': {'responseMimeType': 'application/json', 'responseJsonSchema': schema,
                                 'temperature': 0, 'maxOutputTokens': 2048}}
    request = Request(f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent',
                      data=json.dumps(body).encode(), headers={'x-goog-api-key': api_key,
                      'Content-Type': 'application/json'}, method='POST')
    try:
        with urlopen(request, timeout=45) as response:
            payload = response.read(1_000_001)
    except HTTPError as error:
        raise GeminiError(f'http_{error.code}') from None
    except (URLError, TimeoutError, OSError):
        raise GeminiError('network_error') from None
    if len(payload) > 1_000_000:
        raise GeminiError('response_too_large')
    try:
        result = json.loads(payload)
        candidate = result['candidates'][0]
        if candidate.get('finishReason') != 'STOP':
            raise ValueError('incomplete response')
        text = ''.join(part.get('text', '') for part in candidate['content']['parts'] if not part.get('thought'))
        usage = result.get('usageMetadata', {})
        counts = {key: usage[key] for key in ('promptTokenCount', 'candidatesTokenCount', 'totalTokenCount')
                  if isinstance(usage.get(key), int)}
        return text, counts
    except (KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError):
        raise GeminiError('invalid_response') from None


def request_weights(api_key, model):
    return _request_json(api_key, model, PROMPT, SCHEMA)


def request_repair(api_key, model, warning_type, options):
    prompt = ('Select one numbered repair option for this protein fitness search warning. '
              'Options have different parameter values and costs; all will be checked locally. '
              'Return only the option number.\n' + json.dumps({'warning': warning_type, 'options': options}))
    schema = {'type': 'object', 'properties': {'option': {'type': 'integer', 'minimum': 0,
                                                         'maximum': len(options) - 1}},
              'required': ['option'], 'additionalProperties': False}
    return _request_json(api_key, model, prompt, schema)
