import math
import unittest

from app.experiments.acquisition import acquisition_scores, choose_acquisition


class AcquisitionTests(unittest.TestCase):
    def test_expected_improvement_and_zero_spread(self):
        values = {'a': {'mean': 1.0, 'spread': 1.0}, 'b': {'mean': 2.0, 'spread': 0.0},
                  'c': {'mean': 0.0, 'spread': 0.0}}
        scores = acquisition_scores(values, 1.0, 'ei')
        self.assertAlmostEqual(scores['a'], 1 / math.sqrt(2 * math.pi))
        self.assertEqual(scores['b'], 1.0)
        self.assertEqual(scores['c'], 0.0)
        self.assertEqual(choose_acquisition(scores, 2), ['b', 'a'])

    def test_upper_confidence_and_tie_break(self):
        values = {'b': {'mean': 1.0, 'spread': 1.0}, 'a': {'mean': 2.0, 'spread': 0.0}}
        scores = acquisition_scores(values, 0.0, 'ucb')
        self.assertEqual(choose_acquisition(scores, 2), ['a', 'b'])

    def test_invalid_values_are_rejected(self):
        for mean, spread in [(float('nan'), 1), (0, -1), (True, 1)]:
            with self.subTest(mean=mean, spread=spread), self.assertRaises(ValueError):
                acquisition_scores({'a': {'mean': mean, 'spread': spread}}, 1.0, 'ei')
        with self.assertRaises(ValueError):
            choose_acquisition({'a': 1}, 2)
