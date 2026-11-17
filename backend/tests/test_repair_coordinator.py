import copy
import unittest
from unittest.mock import patch

from app.llm.goal_compiler import DEFAULT_SPEC
from app.experiments.prediction_pilot import run_pilot
from app.rewards.repair_coordinator import handle_warnings


class RepairCoordinatorTests(unittest.TestCase):
    def test_applied_rejected_repair_still_counts_as_failure(self):
        spec = copy.deepcopy(DEFAULT_SPEC)
        revised = copy.deepcopy(spec)
        revised['terms']['distance_penalty']['weight'] = 0.55
        warnings = {kind: {'status': 'triggered' if kind == 'support_shift' else 'not_triggered'}
                    for kind in ('support_shift', 'coverage', 'disagreement', 'diversity')}
        targets = {kind: ['a'] for kind in warnings}
        with patch('app.rewards.repair_coordinator.select_batch', return_value=[{'id': 'a'}]), \
             patch('app.rewards.repair_coordinator.choose_repair', return_value={
                 'status': 'applied_rejected', 'specification': revised, 'attempts': []}):
            result, failures, events, stopped = handle_warnings(
                spec, warnings, targets, {}, 'AAAA', 1, [], [], 1, apply_last_rejected=True)
        self.assertEqual((result, failures, stopped), (revised, 2, True))
        self.assertEqual(events[0]['status'], 'applied_rejected')

    def test_disabled_repair_term_skips_both_uncertainty_routes(self):
        spec = copy.deepcopy(DEFAULT_SPEC)
        warnings = {kind: {'status': 'triggered' if kind in ('coverage', 'disagreement') else 'not_triggered'}
                    for kind in ('support_shift', 'coverage', 'disagreement', 'diversity')}
        targets = {kind: ['a'] for kind in warnings}
        with patch('app.rewards.repair_coordinator.choose_repair') as choose:
            result, failures, events, stopped = handle_warnings(
                spec, warnings, targets, {}, 'AAAA', 1, [], [], 1, disabled_repair_terms=('uncertainty_penalty',))
        choose.assert_not_called()
        self.assertEqual([event['status'] for event in events], ['repair_disabled', 'repair_disabled'])
        self.assertEqual((result, failures, stopped), (spec, 1, False))

    def test_development_without_abstention_keeps_checks_and_continues(self):
        spec = copy.deepcopy(DEFAULT_SPEC)
        warnings = {kind: {'status': 'triggered' if kind in ('support_shift', 'coverage', 'disagreement')
                            else 'not_triggered'}
                    for kind in ('support_shift', 'coverage', 'disagreement', 'diversity')}
        targets = {kind: ['a'] for kind in warnings}
        with patch('app.rewards.repair_coordinator.select_batch', return_value=[{'id': 'a'}]), \
             patch('app.rewards.repair_coordinator.choose_repair', return_value={'status': 'retained',
                   'specification': spec, 'attempts': []}) as choose:
            result, failures, events, stopped = handle_warnings(
                spec, warnings, targets, {}, 'AAAA', 1, [], [], 0, stop_on_failed_repairs=False)
        self.assertFalse(stopped)
        self.assertEqual(failures, 3)
        self.assertEqual(choose.call_count, 3)
        self.assertEqual([event['status'] for event in events], ['retained'] * 3)
        self.assertEqual(result, spec)

    def test_abstention_ablation_is_restricted(self):
        with self.assertRaisesRegex(ValueError, 'restricted'):
            run_pilot('unused', reward_spec=DEFAULT_SPEC, repair=True, dataset='ired', stop_on_failed_repairs=False)
        with self.assertRaisesRegex(ValueError, 'restricted'):
            run_pilot('unused', stop_on_failed_repairs=False)
        with self.assertRaisesRegex(ValueError, 'restricted'):
            run_pilot('unused', reward_spec=DEFAULT_SPEC, repair=True, dataset='ired', bypass_evidence_gate=True)
        with self.assertRaisesRegex(ValueError, 'restricted'):
            run_pilot('unused', bypass_evidence_gate=True)
        with self.assertRaisesRegex(ValueError, 'restricted'):
            run_pilot('unused', reward_spec=DEFAULT_SPEC, repair=True, dataset='ired',
                      disabled_repair_terms=('distance_penalty',))
        with self.assertRaisesRegex(ValueError, 'restricted'):
            run_pilot('unused', reward_spec=DEFAULT_SPEC, repair=True,
                      disabled_repair_terms=('not_a_term',))
        with self.assertRaisesRegex(ValueError, 'restricted'):
            run_pilot('unused', reward_spec=DEFAULT_SPEC, repair=True, dataset='ired', universal_penalty=True)
        with self.assertRaisesRegex(ValueError, 'restricted'):
            run_pilot('unused', reward_spec=DEFAULT_SPEC, repair=True, universal_penalty=True,
                      stop_on_failed_repairs=False)
        with self.assertRaisesRegex(ValueError, 'restricted'):
            run_pilot('unused', reward_spec=DEFAULT_SPEC, repair=True, dataset='ired', apply_last_rejected=True)
        with self.assertRaisesRegex(ValueError, 'restricted'):
            run_pilot('unused', reward_spec=DEFAULT_SPEC, repair=True, apply_last_rejected=True,
                      bypass_evidence_gate=True)

    def test_priority_and_two_failed_repairs_stop(self):
        spec = copy.deepcopy(DEFAULT_SPEC)
        warnings = {kind: {'status': 'triggered'} for kind in ('support_shift', 'coverage', 'disagreement', 'diversity')}
        targets = {kind: ['a'] for kind in warnings}
        with patch('app.rewards.repair_coordinator.select_batch', return_value=[{'id': 'a'}]), \
             patch('app.rewards.repair_coordinator.choose_repair', return_value={'status': 'retained',
                   'specification': spec, 'attempts': []}) as choose:
            result, failures, events, stopped = handle_warnings(spec, warnings, targets, {}, 'AAAA', 1, [], [], 0)
        self.assertTrue(stopped)
        self.assertEqual(failures, 2)
        self.assertEqual([event['warning'] for event in events], ['support_shift', 'coverage'])
        self.assertEqual(choose.call_count, 2)
        self.assertEqual(result, spec)

    def test_no_replayed_targets_does_not_consume_failure(self):
        spec = copy.deepcopy(DEFAULT_SPEC)
        warnings = {kind: {'status': 'not_triggered'} for kind in ('support_shift', 'coverage', 'disagreement', 'diversity')}
        warnings['coverage']['status'] = 'triggered'
        targets = {kind: [] for kind in warnings}
        with patch('app.rewards.repair_coordinator.select_batch', return_value=[{'id': 'a'}]):
            _, failures, events, stopped = handle_warnings(spec, warnings, targets, {}, 'AAAA', 1, [], [], 1)
        self.assertEqual(events[0]['status'], 'no_replayed_targets')
        self.assertEqual(failures, 1)
        self.assertFalse(stopped)

    def test_accepted_change_is_used_next_and_resets_failures(self):
        spec = copy.deepcopy(DEFAULT_SPEC)
        revised = copy.deepcopy(spec)
        revised['terms']['distance_penalty']['weight'] = 0.55
        warnings = {kind: {'status': 'triggered' if kind in ('support_shift', 'coverage') else 'not_triggered'}
                    for kind in ('support_shift', 'coverage', 'disagreement', 'diversity')}
        targets = {kind: ['a'] for kind in warnings}
        responses = [{'status': 'accepted', 'specification': revised, 'attempts': []},
                     {'status': 'retained', 'specification': revised, 'attempts': []}]
        with patch('app.rewards.repair_coordinator.select_batch', return_value=[{'id': 'a'}]), \
             patch('app.rewards.repair_coordinator.choose_repair', side_effect=responses) as choose:
            result, failures, events, stopped = handle_warnings(spec, warnings, targets, {}, 'AAAA', 1, [], [], 1)
        self.assertEqual(choose.call_args_list[1].args[0], revised)
        self.assertEqual([event['consecutive_failures'] for event in events], [0, 1])
        self.assertEqual(result, revised)
        self.assertEqual(failures, 1)
        self.assertFalse(stopped)
