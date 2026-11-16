import json
import unittest
from unittest.mock import patch

from app.llm.gemini_client import GeminiError, request_weights
from app.llm.goal_compiler import DEFAULT_SPEC, compile_goal


class GoalCompilerTests(unittest.TestCase):
    def test_valid_weights_preserve_fixed_constraints(self):
        result = compile_goal(lambda: ('{"uncertainty_penalty":1,"distance_penalty":0.2,"diversity_bonus":0.3}',
                                       {'totalTokenCount': 7}))
        self.assertEqual(result['source'], 'gemini')
        self.assertEqual(result['specification']['hard_constraints'], DEFAULT_SPEC['hard_constraints'])
        self.assertEqual(result['specification']['terms']['uncertainty_penalty']['weight'], 1)

    def test_invalid_response_retried_then_fallback(self):
        attempts = iter([('{"uncertainty_penalty":1,"uncertainty_penalty":2}', {}),
                         ('{"uncertainty_penalty":3,"distance_penalty":0,"diversity_bonus":0}', {})])
        result = compile_goal(lambda: next(attempts))
        self.assertEqual(result['source'], 'fallback')
        self.assertEqual(len(result['attempts']), 2)
        self.assertEqual(result['specification'], DEFAULT_SPEC)

    def test_extra_field_and_nonfinite_rejected(self):
        for text in ('{"uncertainty_penalty":0,"distance_penalty":0,"diversity_bonus":0,"code":"bad"}',
                     '{"uncertainty_penalty":NaN,"distance_penalty":0,"diversity_bonus":0}'):
            with self.subTest(text=text):
                self.assertEqual(compile_goal(lambda: (text, {}))['source'], 'fallback')

    def test_transport_failure_falls_back_without_retry(self):
        def failed():
            raise GeminiError('http_429')
        result = compile_goal(failed)
        self.assertEqual(result['attempts'], [{'status': 'http_429'}])
        self.assertEqual(result['source'], 'fallback')

    def test_request_has_only_fixed_prompt_and_no_key_in_url_or_body(self):
        class Response:
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def read(self, size):
                return json.dumps({'candidates': [{'finishReason': 'STOP', 'content': {'parts': [
                    {'text': '{"uncertainty_penalty":0,"distance_penalty":0,"diversity_bonus":0}'}]}}]}).encode()
        with patch('app.llm.gemini_client.urlopen', return_value=Response()) as send:
            request_weights('sentinel-secret', 'example-model')
        request = send.call_args.args[0]
        self.assertNotIn('sentinel-secret', request.full_url)
        self.assertNotIn('sentinel-secret', request.data.decode())
        self.assertEqual(json.loads(request.data)['contents'][0]['parts'][0]['text'].count('fitness'), 2)

    def test_invalid_model_cannot_alter_destination(self):
        with self.assertRaises(GeminiError):
            request_weights('key', '../unexpected')
