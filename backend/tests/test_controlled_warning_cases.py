"""Hand-labeled boundary examples for two observable warning rules."""
import unittest

from app.rewards.warning_checks import constraint_warning, diversity_warning


class ControlledWarningCases(unittest.TestCase):
    def test_constraint_cases(self):
        candidates = {'unchanged': 'AAAAA', 'one': 'CAAAA', 'four': 'CCCCA', 'five': 'CCCCC'}
        cases = [
            ('one mutation', ['one'], 2, 2, 'not_triggered', None),
            ('four mutations at limit', ['four'], 2, 2, 'not_triggered', None),
            ('five mutations', ['five'], 2, 2, 'triggered', 'mutation_limit'),
            ('two valid at batch limit', ['unchanged', 'one'], 2, 2, 'not_triggered', None),
            ('repeated identifier', ['one', 'one'], 2, 2, 'triggered', 'duplicate'),
            ('unknown identifier', ['unknown'], 2, 2, 'triggered', 'unknown_or_already_revealed'),
            ('one over remaining budget', ['unchanged', 'one'], 1, 2, 'triggered', 'budget_or_batch_limit'),
            ('one over batch size', ['unchanged', 'one'], 2, 1, 'triggered', 'budget_or_batch_limit'),
            ('empty request', [], 2, 2, 'triggered', 'empty_batch'),
            ('mixed valid and invalid', ['one', 'five'], 2, 2, 'triggered', 'mutation_limit'),
        ]
        for name, ids, remaining, limit, expected, reason in cases:
            with self.subTest(case=name):
                result = constraint_warning(ids, candidates, 'AAAAA', remaining, batch_size=limit)
                self.assertEqual((result['status'], result['reason']), (expected, reason))

    def test_diversity_cases(self):
        cases = [
            ('one difference', {'a': 'AAAA', 'b': 'AAAC'}, 'triggered', 1.),
            ('two differences at limit', {'a': 'AAAA', 'b': 'AACC'}, 'not_triggered', 2.),
            ('three differences', {'a': 'AAAA', 'b': 'ACCC'}, 'not_triggered', 3.),
            ('three variants', {'a': 'AAAA', 'b': 'AAAC', 'c': 'AACC'}, 'triggered', 4 / 3),
            ('one variant', {'a': 'AAAA'}, 'unavailable', None),
        ]
        for name, batch, expected, distance in cases:
            with self.subTest(case=name):
                result = diversity_warning(batch)
                self.assertEqual(result['status'], expected)
                if distance is None:
                    self.assertIsNone(result['value'])
                else:
                    self.assertAlmostEqual(result['value'], distance)


if __name__ == '__main__':
    unittest.main()
