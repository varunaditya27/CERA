import unittest

import numpy as np
from scipy.stats import spearmanr

from app.analysis.disagreement_context import group_correlations


class DisagreementContextTests(unittest.TestCase):
    def test_ties_match_independent_pairwise_calculation(self):
        values = np.array([[1, 2, 2, 4], [4, 3, 3, 1], [1, 1, 3, 4],
                           [4, 2, 2, 3], [2, 3, 1, 4]])
        expected = np.mean([spearmanr(values[a], values[b]).statistic
                            for a in range(5) for b in range(a + 1, 5)])
        self.assertAlmostEqual(group_correlations(values), expected)

    def test_constant_member_is_unavailable(self):
        self.assertIsNone(group_correlations([[1, 1, 1], [1, 2, 3], [1, 3, 2],
                                              [2, 1, 3], [3, 2, 1]]))

    def test_invalid_values_are_rejected(self):
        with self.assertRaises(ValueError):
            group_correlations([[float('nan'), 1]] * 5)
