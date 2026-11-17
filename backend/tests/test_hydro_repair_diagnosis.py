import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
from diagnose_hydro_repairs import analyze_actions


def attempt(accepted, checks):
    return {'verification': {'accepted': accepted, 'checks': checks}}


def action(status, count, warning='coverage', attempts=None):
    return {'warning': warning, 'status': status, 'consecutive_failures': count,
            'attempts': attempts if attempts is not None else []}


def batch(number, actions, count):
    return {'event': 'method', 'settings': {'round': number, 'repair_actions': actions, 'consecutive_failures': count}}


def records(actions, stop='failed_repairs'):
    return [{'event': 'method', 'settings': {'repair': True, 'reward_spec': {'abstain_after_failed_repairs': 2}}},
            *actions, {'event': 'stop', 'stop_reason': stop}]


class RepairDiagnosisTest(unittest.TestCase):
    def test_overlapping_checks_same_batch_and_empty_menu(self):
        rejected = attempt(False, {'displacement': False, 'rank': False, 'coverage': None})
        events = records([batch(1, [action('retained', 1, attempts=[rejected]),
                                    action('retained', 2, 'disagreement')], 2)])
        result = analyze_actions(events)
        self.assertTrue(result['final_failures_same_batch'])
        self.assertEqual(result['empty_menu_actions'], 1)
        self.assertEqual(result['failed_checks']['coverage'],
                         {'coverage:unavailable': 1, 'displacement:false': 1, 'rank:false': 1})
        self.assertEqual(sum(result['attempts'].values()), 1)

    def test_reset_noop_and_different_batches(self):
        rejected = attempt(False, {'safe': False})
        accepted = attempt(True, {'safe': True})
        noop = {'warning': 'diversity', 'status': 'no_replayed_targets'}
        events = records([batch(1, [action('retained', 1, attempts=[rejected]),
                                    action('accepted', 0, attempts=[accepted]), noop], 0),
                          batch(2, [action('retained', 1, attempts=[rejected])], 1),
                          batch(3, [action('retained', 2, 'disagreement', [rejected])], 2)])
        result = analyze_actions(events)
        self.assertFalse(result['final_failures_same_batch'])
        self.assertEqual(result['accepted_actions'], 1)
        self.assertEqual([f['round'] for f in result['final_failures']], [2, 3])
        altered = copy.deepcopy(events)
        altered[2]['settings']['consecutive_failures'] = 7
        with self.assertRaisesRegex(ValueError, 'counter mismatch'):
            analyze_actions(altered)
        altered = copy.deepcopy(events)
        altered[-1]['stop_reason'] = 'budget_exhausted'
        with self.assertRaisesRegex(ValueError, 'Stop does not match'):
            analyze_actions(altered)

    def test_rejects_inconsistent_acceptance(self):
        bad = attempt(True, {'safe': False})
        with self.assertRaisesRegex(ValueError, 'Inconsistent verification'):
            analyze_actions(records([batch(1, [action('accepted', 0, attempts=[bad])], 0)], 'budget_exhausted'))


if __name__ == '__main__':
    unittest.main()
