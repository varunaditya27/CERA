import copy
import unittest

from app.experiments.evaluation import evaluate


class EvaluationTests(unittest.TestCase):
    def setUp(self):
        self.scores = {'a': 1.0, 'b': 3.0, 'c': 2.0}
        self.events = [{'event': 'start', 'data_sha256': 'data', 'reference_sha256': 'ref',
                        'initial': {'a': 1.0}, 'initial_count': 1, 'budget': 2, 'batch_size': 1,
                        'stop_reason': None},
                       {'event': 'selection', 'ids': ['c'], 'prediction_ranges': {'c': {'lower': 1, 'upper': 2}}},
                       {'event': 'reveal', 'measurements': {'c': 2.0}, 'remaining': 1, 'stop_reason': None},
                       {'event': 'stop', 'remaining': 1, 'stop_reason': 'failed_repairs'}]

    def run_evaluation(self, events):
        return evaluate(events, self.scores, {'a'}, 'data', 'ref')

    def test_regret_range_boundary_and_early_stop(self):
        result = self.run_evaluation(self.events)
        self.assertEqual([row['pool_regret'] for row in result['curve']], [2, 1])
        self.assertEqual(result['stop_reason'], 'failed_repairs')
        self.assertEqual(result['covered'], 1)
        self.assertEqual(result['range_count'], 1)
        self.assertEqual(result['mean_range_width'], 1)
        self.assertFalse(result['curve'][-1]['found_top_one_percent'])

    def test_random_ranges_are_unavailable(self):
        events = copy.deepcopy(self.events)
        del events[1]['prediction_ranges']
        result = self.run_evaluation(events)
        self.assertIsNone(result['covered'])
        self.assertIsNone(result['mean_range_width'])

    def test_no_neighbors_is_an_explicit_early_stop(self):
        events = copy.deepcopy(self.events)
        events[-1]['stop_reason'] = 'no_neighbors'
        self.assertEqual(self.run_evaluation(events)['stop_reason'], 'no_neighbors')

    def test_bad_fingerprint_duplicate_wrong_score_and_incomplete_are_rejected(self):
        cases = []
        bad = copy.deepcopy(self.events); bad[0]['data_sha256'] = 'other'; cases.append(bad)
        bad = copy.deepcopy(self.events); bad[1]['ids'] = ['a']; cases.append(bad)
        bad = copy.deepcopy(self.events); bad[2]['measurements']['c'] = 5; cases.append(bad)
        cases.append(self.events[:-1])
        for events in cases:
            with self.subTest(events=events), self.assertRaises(ValueError):
                self.run_evaluation(events)
