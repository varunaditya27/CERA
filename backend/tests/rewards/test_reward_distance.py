import unittest

from app.rewards.reward_distance import known_distances, normalized_distances


class RewardDistanceTests(unittest.TestCase):
    def test_nearest_other_scaling_and_clipping(self):
        vectors = {'a': [0.0], 'b': [2.0], 'c': [5.0], 'x': [1.0], 'y': [10.0]}
        result = normalized_distances(['a', 'b', 'c'], ['x', 'y'], vectors)
        self.assertEqual(result['scale'], 3.0)
        self.assertAlmostEqual(result['distances']['x'], 1 / 3)
        self.assertEqual(result['distances']['y'], 1.0)
        self.assertEqual(known_distances(['a', 'b', 'c'], vectors), {'a': 2 / 3, 'b': 2 / 3, 'c': 1.0})

    def test_degenerate_known_set_is_rejected(self):
        with self.assertRaises(ValueError):
            normalized_distances(['a', 'b'], ['x'], {'a': [0], 'b': [0], 'x': [1]})

    def test_overlapping_ids_and_invalid_vectors_are_rejected(self):
        vectors = {'a': [0.0], 'b': [1.0], 'x': [float('nan')]}
        with self.assertRaises(ValueError):
            normalized_distances(['a', 'b'], ['a'], vectors)
        with self.assertRaises(ValueError):
            normalized_distances(['a', 'b'], ['x'], vectors)
