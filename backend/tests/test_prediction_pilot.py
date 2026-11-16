import csv
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
from sklearn.linear_model import RidgeCV

from app.features.amylase_representations import load_verified_representations
from app.experiments.experiment import Experiment
from app.experiments.prediction_intervals import batch_coverage, interval_radius
from app.experiments.predictor_group import fit_group, predict_group
from app.experiments.range_report import summarize_ranges


class RestrictedScores(dict):
    def __getitem__(self, key):
        if key == 'reserved':
            raise AssertionError('Reserved score was used for fitting')
        return super().__getitem__(key)


class PredictionPilotTests(unittest.TestCase):
    def test_group_uses_only_unique_fitting_examples_before_bootstrap(self):
        ids = [f'id-{i}' for i in range(10)]
        vectors = {identifier: np.array([i, i * i], dtype=float) for i, identifier in enumerate(ids)}
        vectors['reserved'] = np.array([100, 100])
        scores = RestrictedScores({identifier: float(i) for i, identifier in enumerate(ids)})
        scores['reserved'] = 999.0
        original_fit = RidgeCV.fit
        observed = []

        def capture(model, x, y, *args, **kwargs):
            observed.append((x.copy(), y.copy()))
            return original_fit(model, x, y, *args, **kwargs)

        with patch.object(RidgeCV, 'fit', capture):
            first, penalty = fit_group(vectors, scores, ids, ['reserved'], 1, [1, 2, 3, 4, 5])
        second, other_penalty = fit_group(vectors, scores, ids, ['reserved'], 1, [1, 2, 3, 4, 5])
        self.assertEqual(len(observed), 1)
        self.assertEqual(len(np.unique(observed[0][0], axis=0)), len(ids))
        self.assertEqual(penalty, other_penalty)
        first_mean, first_spread = predict_group(first, vectors, ids)
        second_mean, second_spread = predict_group(second, vectors, ids)
        np.testing.assert_array_equal(first_mean, second_mean)
        np.testing.assert_array_equal(first_spread, second_spread)
        self.assertTrue(np.all(first_spread >= 0))
        with self.assertRaises(ValueError):
            fit_group(vectors, scores, ids + ['reserved'], ['reserved'], 1, [1, 2, 3, 4, 5])

    def test_interval_order_statistic_ties_and_invalid_inputs(self):
        self.assertEqual(interval_radius(np.zeros(20), np.arange(1, 21)), 19.0)
        self.assertEqual(interval_radius(np.zeros(20), [1] * 19 + [5]), 1.0)
        for predictions, scores in (([], []), ([0] * 8, [1] * 8), ([0], [float('nan')]), ([1], [1, 2])):
            with self.subTest(scores=scores), self.assertRaises(ValueError):
                interval_radius(predictions, scores)
        self.assertEqual(batch_coverage({'a': {'lower': 1., 'upper': 3.}}, {'a': 3.}), (1, 1, 2.))

    def test_ranges_recorded_before_reveal_and_coverage_reconstructed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'reference').write_text('>reference\nAAAA\n')
            with (root / 'data.csv').open('w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['sequence', 'target', 'set', 'validation'])
                writer.writerows([('AAAA', 1, 'train', 'False'), ('CAAA', 2, 'test', 'False'),
                                  ('ACAA', 3, 'test', 'False')])
            run = Experiment(root / 'data.csv', root / 'reference', root / 'run.jsonl', 1,
                             initial_count=1, budget=2, batch_size=2)
            self.addCleanup(run.close)
            candidates = list(run.candidates)
            ranges = {identifier: {'mean': 2., 'spread': 0.5, 'lower': 1., 'upper': 2.5}
                      for identifier in candidates}
            invalid = {identifier: dict(value) for identifier, value in ranges.items()}
            invalid[candidates[0]]['spread'] = -1
            with self.assertRaises(ValueError):
                run.reveal(candidates, prediction_ranges=invalid)
            self.assertEqual(run.remaining, 2)
            with self.assertRaises(ValueError):
                run.reveal(candidates, prediction_ranges={candidates[0]: ranges[candidates[0]]})
            self.assertEqual(run.remaining, 2)
            run.reveal(candidates, prediction_ranges=ranges)
            events = [json.loads(line) for line in (root / 'run.jsonl').read_text().splitlines()]
            self.assertEqual([event['event'] for event in events], ['start', 'selection', 'reveal'])
            self.assertEqual(events[1]['prediction_ranges'], ranges)
            rows = summarize_ranges(root / 'run.jsonl', root / 'coverage.csv')
            self.assertEqual(rows[0][2:6], (1, 2, 0.5, 1.5))
            self.assertEqual(rows[0][6:9], (1, 2, 0.5))
            (root / 'partial.jsonl').write_text('\n'.join(json.dumps(event) for event in events[:2]) + '\n')
            with self.assertRaises(ValueError):
                summarize_ranges(root / 'partial.jsonl', root / 'partial.csv')

    def test_cache_fingerprint_rejects_wrong_cache(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'wrong.npz'
            path.write_bytes(b'not the pinned cache')
            with self.assertRaises(ValueError):
                load_verified_representations(cache_path=path)
            wrong_data = Path(directory) / 'wrong.csv'
            wrong_data.write_text('sequence\nAAAA\n')
            with self.assertRaises(ValueError):
                load_verified_representations(data_path=wrong_data)
        vectors = load_verified_representations()
        self.assertEqual(len(vectors), 3706)
        self.assertEqual(next(iter(vectors.values())).shape, (320,))


if __name__ == '__main__':
    unittest.main()
