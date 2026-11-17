import copy
import math
import random
import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
from evaluate_heldout_shifts import evaluate_run
from app.analysis.heldout_prediction import predict_heldout
from app.experiments.predictor_group import fit_group, predict_group


class HeldoutPredictionTest(unittest.TestCase):
    def setUp(self):
        self.train = [f'train-{i:03}' for i in range(110)]
        self.test = ['test-1', 'test-2', 'test-3']
        self.vectors = {name: np.array([i, i % 7, i % 11], dtype=float) / 100
                        for i, name in enumerate(self.train + self.test)}
        self.scores = {name: i / 100 for i, name in enumerate(self.train + self.test)}
        self.initial = random.Random(121).sample(self.train, 100)
        self.selected = {i: self.scores[i] for i in self.initial}

    def test_heldout_scores_not_given_and_calibration_reconstructed(self):
        result = predict_heldout(self.vectors, self.selected, self.test, 121)
        altered_scores = dict(self.scores, **{'test-1': 1000})
        self.assertEqual(result, predict_heldout(self.vectors, self.selected, self.test, 121))
        fitting = sorted(set(self.initial) - set(result['reserved_ids']))
        models, _ = fit_group(self.vectors, self.selected, fitting, result['reserved_ids'], 121,
                              result['member_seeds'])
        means, _ = predict_group(models, self.vectors, result['reserved_ids'])
        errors = sorted(abs(self.selected[i] - p) for i, p in zip(result['reserved_ids'], means))
        self.assertAlmostEqual(result['radius'], errors[math.ceil(21 * .9) - 1])
        self.assertNotEqual(evaluate_run(result, self.train, self.test, self.scores)['mean_absolute_error'],
                            evaluate_run(result, self.train, self.test, altered_scores)['mean_absolute_error'])
        with self.assertRaises(ValueError):
            predict_heldout(self.vectors, dict(self.selected, **{'test-1': 1000}), self.test, 121)

    def test_rejects_tampered_predictions_and_roles(self):
        result = predict_heldout(self.vectors, self.selected, self.test, 121)
        for change in ('missing', 'duplicate', 'nonfinite', 'roles'):
            altered = copy.deepcopy(result)
            if change == 'missing': altered['predictions'].pop()
            elif change == 'duplicate': altered['predictions'][0][0] = altered['predictions'][1][0]
            elif change == 'nonfinite': altered['predictions'][0][1] = float('nan')
            else: altered['reserved_ids'][0] = 'test-1'
            with self.subTest(change=change), self.assertRaises(ValueError):
                evaluate_run(altered, self.train, self.test, self.scores)


if __name__ == '__main__':
    unittest.main()
