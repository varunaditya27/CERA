import unittest

from app.analysis.disagreement_ranking import evaluate


def records(measured):
    ids = ['a', 'b', 'c']
    source = [{'event': 'selection', 'ids': ids, 'prediction_ranges':
               {identifier: {'mean': value} for identifier, value in zip(ids, [1., 2., 3.])}},
              {'event': 'reveal', 'measurements': dict(zip(ids, measured))}]
    replay = [{'event': 'warning', 'type': 'disagreement', 'round': 1, 'stage': 'pre_reveal',
               'status': 'triggered', 'identifiers': ids},
              {'event': 'reveal_reference', 'round': 1, 'identifiers': ids}]
    return source, replay


class DisagreementRankingTests(unittest.TestCase):
    def test_rankings_and_constant(self):
        self.assertAlmostEqual(evaluate(*records([1., 2., 3.]))[0]['spearman'], 1.)
        self.assertAlmostEqual(evaluate(*records([3., 2., 1.]))[0]['spearman'], -1.)
        self.assertAlmostEqual(evaluate(*records([1., 1., 2.]))[0]['spearman'], 0.8660254037844387)
        self.assertIsNone(evaluate(*records([1., 1., 1.]))[0]['spearman'])

    def test_rejects_invalid_chronology_and_mismatched_groups(self):
        source, replay = records([1., 2., 3.])
        with self.assertRaises(ValueError):
            evaluate(source, list(reversed(replay)))
        source, replay = records([1., 2., 3.])
        replay[0]['identifiers'] = ['a']
        with self.assertRaises(ValueError):
            evaluate(source, replay)
        source, replay = records([1., 2., 3.])
        source[1]['measurements']['a'] = float('nan')
        with self.assertRaises(ValueError):
            evaluate(source, replay)


if __name__ == '__main__':
    unittest.main()
