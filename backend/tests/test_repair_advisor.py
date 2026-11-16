import copy
import unittest
from unittest.mock import patch

from app.llm.gemini_client import GeminiError
from app.llm.goal_compiler import DEFAULT_SPEC
from app.llm.repair_advisor import advise_repair
from app.rewards.repair_engine import choose_repair
from app.rewards.repair_menu import repair_candidates


class RepairAdvisorTests(unittest.TestCase):
    def setUp(self):
        self.spec = copy.deepcopy(DEFAULT_SPEC)
        self.menu = repair_candidates(self.spec, 'disagreement')

    def test_only_sanitized_menu_sent_and_valid_choice_recorded(self):
        seen = []
        def request(kind, options):
            seen.append((kind, options))
            return '{"option":2}', {'totalTokenCount': 10}
        result = advise_repair(request, 'disagreement', self.menu)
        self.assertEqual(result['source'], 'gemini')
        self.assertEqual(result['option'], 2)
        self.assertEqual(set(seen[0][1][0]), {'option', 'term', 'weight', 'cost'})
        self.assertNotIn('specification', str(seen))

    def test_invalid_or_duplicate_choice_retries_and_falls_back(self):
        responses = iter([('{"option":true}', {}), ('{"option":1,"option":2}', {})])
        result = advise_repair(lambda *_: next(responses), 'disagreement', self.menu)
        self.assertEqual(result['source'], 'fallback')
        self.assertEqual(result['option'], 0)
        self.assertEqual(len(result['attempts']), 2)

    def test_transport_failure_falls_back_once(self):
        def failed(*_):
            raise GeminiError('http_429')
        result = advise_repair(failed, 'disagreement', self.menu)
        self.assertEqual(result['attempts'], [{'status': 'http_429'}])

    def test_model_preference_is_checked_then_remaining_options_in_cost_order(self):
        checks = [{'accepted': False}, {'accepted': True}]
        advisor = lambda kind, menu: {'option': 2, 'source': 'gemini'}
        with patch('app.rewards.repair_engine.verify_repair', side_effect=checks) as verify:
            result = choose_repair(self.spec, 'disagreement', {}, 'AAAA', 1, [], [], [], advisor=advisor)
        self.assertEqual([x['proposed_weight'] for x in result['attempts']], [1.5, 0.75])
        self.assertEqual(verify.call_count, 2)
        self.assertEqual(result['specification']['terms']['uncertainty_penalty']['weight'], 0.75)

    def test_out_of_range_advisor_choice_is_rejected(self):
        with self.assertRaises(ValueError):
            choose_repair(self.spec, 'disagreement', {}, 'AAAA', 1, [], [], [],
                          advisor=lambda *_: {'option': 99})
