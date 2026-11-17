import copy
import unittest
from unittest.mock import patch

from app.llm.goal_compiler import DEFAULT_SPEC
from app.rewards.repair_engine import choose_repair
from app.rewards.repair_menu import repair_candidates
from app.rewards.repair_verification import verify_repair


def fixture():
    spec = copy.deepcopy(DEFAULT_SPEC)
    for term in spec['terms'].values():
        term['weight'] = 0.0
    spec['budget']['batch_size'] = 1
    candidates = {'a': {'sequence': 'AAAA', 'mean': 1.0, 'spread': 1.0, 'distance': 0.9},
                  'b': {'sequence': 'AAAC', 'mean': 0.9, 'spread': 0.0, 'distance': 0.0}}
    calibration = [{'lower': 0.0, 'upper': 1.0, 'score': 0.5} for _ in range(18)]
    calibration += [{'lower': 0.0, 'upper': 1.0, 'score': 2.0} for _ in range(2)]
    earlier = [{'mean': float(i), 'spread': 0.0, 'distance': 0.0, 'score': float(i)}
               for i in range(5)]
    return spec, candidates, calibration, earlier


class RepairTests(unittest.TestCase):
    def test_bypassing_evidence_gate_keeps_menu_guard(self):
        spec, candidates, calibration, earlier = fixture()
        normal = choose_repair(spec, 'support_shift', candidates, 'AAAA', 1, ['a'], calibration[:19], earlier)
        ablated = choose_repair(spec, 'support_shift', candidates, 'AAAA', 1, ['a'], calibration[:19], earlier,
                                bypass_evidence_gate=True)
        self.assertEqual(normal['status'], 'retained')
        self.assertEqual(ablated['status'], 'accepted')
        self.assertFalse(ablated['attempts'][0]['verification']['accepted'])
        self.assertTrue(ablated['attempts'][0]['verification']['checks']['allowed_change_and_constraints'])
        with patch('app.rewards.repair_engine.verify_repair', return_value={
                'accepted': False, 'checks': {'allowed_change_and_constraints': False}}):
            guarded = choose_repair(spec, 'support_shift', candidates, 'AAAA', 1, ['a'], calibration, earlier,
                                    bypass_evidence_gate=True)
        self.assertEqual(guarded['status'], 'retained')

    def test_chooses_cheapest_checked_change_without_mutating_old_spec(self):
        spec, candidates, calibration, earlier = fixture()
        original = copy.deepcopy(spec)
        result = choose_repair(spec, 'support_shift', candidates, 'AAAA', 1, ['a'], calibration, earlier)
        self.assertEqual(result['status'], 'accepted')
        self.assertEqual(len(result['attempts']), 1)
        self.assertEqual(result['specification']['terms']['distance_penalty']['weight'], 0.25)
        self.assertAlmostEqual(result['attempts'][0]['cost'], 0.175)
        self.assertEqual(spec, original)
        self.assertTrue(all(result['attempts'][0]['verification']['checks'].values()))

    def test_missing_evidence_and_no_repair_keep_old_rule(self):
        spec, candidates, calibration, earlier = fixture()
        result = choose_repair(spec, 'support_shift', candidates, 'AAAA', 1, ['a'], calibration[:19], earlier)
        self.assertEqual(result['status'], 'retained')
        self.assertEqual(result['specification'], spec)
        self.assertIsNone(result['attempts'][0]['verification']['checks']['calibration_coverage'])
        spec['terms']['distance_penalty']['weight'] = 2.0
        self.assertEqual(repair_candidates(spec, 'support_shift'), [])

    def test_bad_constraints_and_undisplaced_cases_fail(self):
        spec, candidates, calibration, earlier = fixture()
        proposed = copy.deepcopy(spec)
        proposed['terms']['distance_penalty']['weight'] = 0.01
        proposed['hard_constraints']['max_mutations'] = 3
        result = verify_repair(spec, proposed, 'support_shift', candidates, 'AAAA', 1, ['a'], calibration, earlier)
        self.assertFalse(result['checks']['allowed_change_and_constraints'])
        self.assertFalse(result['checks']['counterexamples_displaced'])
        self.assertFalse(result['accepted'])

    def test_constant_ranking_is_unavailable_and_false_evidence_is_rejected(self):
        spec, candidates, calibration, earlier = fixture()
        proposed = repair_candidates(spec, 'support_shift')[0]['specification']
        for row in earlier:
            row['score'] = 1.0
        result = verify_repair(spec, proposed, 'support_shift', candidates, 'AAAA', 1, ['a'], calibration, earlier)
        self.assertIsNone(result['checks']['earlier_rank_preserved'])
        self.assertFalse(result['accepted'])
        with self.assertRaises(ValueError):
            verify_repair(spec, proposed, 'support_shift', candidates, 'AAAA', 1, ['b'], calibration, earlier)
        calibration[0]['score'] = float('nan')
        with self.assertRaises(ValueError):
            verify_repair(spec, proposed, 'support_shift', candidates, 'AAAA', 1, ['a'], calibration, earlier)

    def test_direct_diversity_accepts_resolved_batch_without_removing_every_target(self):
        spec, candidates, calibration, earlier = fixture()
        spec['budget']['batch_size'] = 2
        candidates['a'].update(spread=0.0, distance=0.0)
        candidates['c'] = {'sequence': 'CCAA', 'mean': 0.85, 'spread': 0.0, 'distance': 0.0}
        proposed = repair_candidates(spec, 'diversity')[0]['specification']
        old = verify_repair(spec, proposed, 'diversity', candidates, 'AAAA', 2, ['a', 'b'], calibration, earlier)
        new = verify_repair(spec, proposed, 'diversity', candidates, 'AAAA', 2, ['a', 'b'], calibration, earlier,
                            direct_diversity=True)
        self.assertFalse(old['accepted'])
        self.assertEqual(new['replayed_ids'], ['a', 'c'])
        self.assertTrue(new['checks']['diversity_resolved'])
        self.assertTrue(new['accepted'])
        candidates['c']['sequence'] = 'AACA'
        unresolved = verify_repair(spec, proposed, 'diversity', candidates, 'AAAA', 2, ['a', 'b'], calibration, earlier,
                                   direct_diversity=True)
        self.assertFalse(unresolved['checks']['diversity_resolved'])
        self.assertFalse(unresolved['accepted'])

    def test_direct_diversity_rejects_unavailable_or_missing_calibration(self):
        spec, candidates, calibration, earlier = fixture()
        proposed = repair_candidates(spec, 'diversity')[0]['specification']
        result = verify_repair(spec, proposed, 'diversity', candidates, 'AAAA', 1, ['a'], calibration, earlier,
                               direct_diversity=True)
        self.assertIsNone(result['checks']['diversity_resolved'])
        self.assertFalse(result['accepted'])
        spec['budget']['batch_size'] = 2
        candidates['c'] = {'sequence': 'CCAA', 'mean': 0.85, 'spread': 0.0, 'distance': 0.0}
        proposed = repair_candidates(spec, 'diversity')[0]['specification']
        result = verify_repair(spec, proposed, 'diversity', candidates, 'AAAA', 2, ['a', 'b'], calibration[:19], earlier,
                               direct_diversity=True)
        self.assertIsNone(result['checks']['calibration_coverage'])
        self.assertFalse(result['accepted'])

    def test_rejects_coverage_and_ranking_regressions(self):
        spec, candidates, calibration, earlier = fixture()
        proposed = repair_candidates(spec, 'support_shift')[0]['specification']
        calibration[0]['score'] = calibration[1]['score'] = calibration[2]['score'] = 2.0
        for i, row in enumerate(earlier):
            row['mean'] = 0.05 * i
            row['distance'] = i / 4
        result = verify_repair(spec, proposed, 'support_shift', candidates, 'AAAA', 1, ['a'], calibration, earlier)
        self.assertFalse(result['checks']['calibration_coverage'])
        self.assertFalse(result['checks']['earlier_rank_preserved'])
        self.assertFalse(result['accepted'])
