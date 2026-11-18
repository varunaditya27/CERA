import unittest

from app.rewards.disagreement_targets import disagreement_targets


class DisagreementTargetTests(unittest.TestCase):
    def test_opposite_and_identical_rankings_and_unassessed(self):
        warning = {'status': 'triggered', 'identifiers': ['a', 'b', 'c'], 'evidence': {'members': {
            'a': [1, 3, 1, 3, 1], 'b': [2, 2, 2, 2, 2], 'c': [3, 1, 3, 1, 3]}}}
        result = disagreement_targets(warning, ['a', 'b', 'outside'])
        self.assertEqual(result['targets'], ['a'])
        self.assertEqual(result['assessed'], {'a': 1.0, 'b': 0.0})
        self.assertEqual(result['unassessed'], ['outside'])

    def test_tied_ranks_at_boundary(self):
        warning = {'status': 'triggered', 'identifiers': ['a', 'b', 'c'], 'evidence': {'members': {
            'a': [1, 1, 1, 1, 2], 'b': [1, 2, 2, 2, 1], 'c': [3, 3, 3, 3, 3]}}}
        result = disagreement_targets(warning, ['a', 'b', 'c'])
        self.assertEqual(result['assessed']['a'], 0.5)
        self.assertEqual(result['assessed']['b'], 0.5)
        self.assertEqual(result['targets'], ['a', 'b'])
        warning['evidence']['members'] = {'a': [1, 1, 1, 1, 1], 'b': [1, 2, 2, 2, 3],
                                           'c': [3, 3, 3, 3, 2]}
        result = disagreement_targets(warning, ['a', 'b'])
        self.assertEqual(result['assessed']['a'], 0.25)
        self.assertEqual(result['targets'], ['b'])

    def test_unavailable_or_nontriggered_never_creates_targets(self):
        for status in ('unavailable', 'not_triggered'):
            result = disagreement_targets({'status': status}, ['a'])
            self.assertEqual(result['targets'], [])
            self.assertEqual(result['unassessed'], ['a'])

    def test_invalid_or_constant_evidence_rejected(self):
        warning = {'status': 'triggered', 'identifiers': ['a', 'b'], 'evidence': {'members': {
            'a': [1, 1, 1, 1, 1], 'b': [1, 2, 2, 2, 2]}}}
        with self.assertRaises(ValueError):
            disagreement_targets(warning, ['a'])
        with self.assertRaises(ValueError):
            disagreement_targets(warning, ['a', 'a'])
