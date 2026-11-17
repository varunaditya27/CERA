import unittest
import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

from app.analysis.additional_metrics import evaluate

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
import evaluate_additional_metrics


def fixture():
    sequences = {str(i): f'{i:03d}' for i in range(101)}
    scores = {str(i): (10. if i < 3 else 0.) for i in range(101)}
    events = [{'event': 'start', 'initial': {'0': 10.}},
              {'event': 'selection', 'ids': ['1', '3'], 'prediction_ranges':
               {'1': {'mean': 1.}, '3': {'mean': 0.}}},
              {'event': 'reveal', 'measurements': {'1': 10., '3': 0.}},
              {'event': 'selection', 'ids': ['4']},
              {'event': 'reveal', 'measurements': {'4': 0.}}]
    return events, sequences, scores


class AdditionalMetricsTests(unittest.TestCase):
    def test_incomplete_study_does_not_load_score_pool(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'manifest.json').write_text(json.dumps({'dataset': 'ired', 'initial_pool': 'eligible',
                                                           'seeds': [1], 'methods': ['random']}))
            argv = ['evaluate_additional_metrics.py', str(root / 'report.json'), str(root), '--specification', 'unused']
            with patch.object(sys, 'argv', argv), patch.object(evaluate_additional_metrics, 'dataset_source') as source, \
                 self.assertRaisesRegex(ValueError, 'terminal statuses'):
                evaluate_additional_metrics.main()
            source.assert_not_called()

    def test_tied_top_cutoff_initial_and_new(self):
        result = evaluate(*fixture())
        self.assertEqual((result['top_count'], result['initial_top_found'], result['new_top_found']), (3, 1, 1))
        self.assertEqual(result['top_recall'], 2 / 3)
        self.assertEqual((result['new_measurements'], result['cumulative_regret']), (3, 20.))
        self.assertAlmostEqual(result['mean_new_regret'], 20 / 3)
        self.assertAlmostEqual(result['batches'][0]['prediction_score_spearman'], 1.)
        self.assertEqual(result['batches'][0]['mean_pairwise_differences'], 1.)
        self.assertIsNone(result['batches'][1]['prediction_score_spearman'])
        self.assertIsNone(result['batches'][1]['mean_pairwise_differences'])

    def test_constant_rank_and_invalid_records(self):
        events, sequences, scores = fixture()
        events[1]['prediction_ranges']['1']['mean'] = 0.
        self.assertIsNone(evaluate(events, sequences, scores)['batches'][0]['prediction_score_spearman'])
        events, sequences, scores = fixture()
        events[2]['measurements']['1'] = 9.
        with self.assertRaisesRegex(ValueError, 'source'):
            evaluate(events, sequences, scores)
        events, sequences, scores = fixture()
        events[3]['ids'] = ['1']
        with self.assertRaisesRegex(ValueError, 'selection'):
            evaluate(events, sequences, scores)

    def test_all_tied_pool_has_full_denominator(self):
        events, sequences, scores = fixture()
        scores = dict.fromkeys(scores, 0.)
        events[0]['initial']['0'] = 0.
        events[2]['measurements']['1'] = 0.
        result = evaluate(events, sequences, scores)
        self.assertEqual(result['top_count'], 101)
        self.assertEqual(result['top_recall'], 4 / 101)
        self.assertIsNone(result['batches'][0]['prediction_score_spearman'])

    def test_first_accepted_repair_and_later_window(self):
        events, sequences, scores = fixture()
        self.assertEqual(evaluate(events, sequences, scores)['post_first_repair']['status'], 'no_accepted_repair')
        accepted = {'event': 'method', 'settings': {'repair_actions': [{'status': 'accepted'}]}}
        events.insert(3, accepted)
        events[4]['prediction_ranges'] = {'4': {'mean': 0., 'lower': 0., 'upper': 0.}}
        self.assertEqual(evaluate(events, sequences, scores)['post_first_repair']['status'], 'insufficient_followup')
        ids = [str(i) for i in range(4, 34)]
        ranges = {identifier: {'mean': 0., 'lower': 0., 'upper': 0.} for identifier in ids}
        for identifier in ids[:3]:
            ranges[identifier] = {'mean': 1., 'lower': 1., 'upper': 1.}
        events[4:] = [{'event': 'selection', 'ids': ids, 'prediction_ranges': ranges},
                      {'event': 'reveal', 'measurements': {identifier: scores[identifier] for identifier in ids}}]
        post = evaluate(events, sequences, scores)['post_first_repair']
        self.assertEqual((post['status'], post['accepted_after_measurements'], post['later_measurements']),
                         ('observed', 2, 30))
        self.assertEqual(post['first_30_covered'], 27)
        self.assertTrue(post['first_30_in_target_band'])


if __name__ == '__main__':
    unittest.main()
