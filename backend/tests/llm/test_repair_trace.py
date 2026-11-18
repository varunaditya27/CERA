import unittest
from unittest.mock import patch

from app.llm.gemini_client import GeminiError
from app.llm.repair_trace import traced_repair_advice


class RepairTraceTests(unittest.TestCase):
    def test_records_invalid_reply_then_accepted_reply(self):
        candidate = {'term': 'distance_penalty', 'cost': 0.2,
                     'specification': {'terms': {'distance_penalty': {'weight': 0.5}}}}
        replies = iter([('bad reply', {}), ('{"option":0}', {'totalTokenCount': 3})])
        result = traced_repair_advice(lambda warning, options: next(replies), 'support_shift', [candidate])
        self.assertEqual(result['source'], 'gemini')
        self.assertEqual([entry['response'] for entry in result['transcript']], ['bad reply', '{"option":0}'])
        self.assertEqual(result['transcript'][0]['warning'], 'support_shift')
        self.assertEqual(result['transcript'][0]['options'], result['options'])

    def test_records_failure_without_secrets(self):
        candidate = {'term': 'distance_penalty', 'cost': 0.2,
                     'specification': {'terms': {'distance_penalty': {'weight': 0.5}}}}
        def fail(warning, options):
            raise GeminiError('network_error')
        result = traced_repair_advice(fail, 'support_shift', [candidate])
        self.assertEqual(result['source'], 'fallback')
        self.assertEqual(result['transcript'][0]['error'], 'network_error')
        self.assertNotIn('response', result['transcript'][0])

    @patch('app.llm.local_advisor.request_repair', return_value=('{"option":0}', {}))
    @patch('app.llm.local_advisor.local_gemini_configuration', return_value=('private-key', 'test-model'))
    def test_local_advisor_keeps_trace_without_credentials(self, configuration, request):
        from app.llm.local_advisor import local_repair_advisor
        candidate = {'term': 'distance_penalty', 'cost': 0.2,
                     'specification': {'terms': {'distance_penalty': {'weight': 0.5}}}}
        advisor, model = local_repair_advisor()
        result = advisor('support_shift', [candidate])
        self.assertEqual(model, 'test-model')
        self.assertEqual(result['transcript'][0]['response'], '{"option":0}')
        self.assertNotIn('private-key', str(result))


if __name__ == '__main__':
    unittest.main()
