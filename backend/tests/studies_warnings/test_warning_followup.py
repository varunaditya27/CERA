import unittest

from app.analysis.warning_followup import evaluate, summarize


def records():
    source, replay = [], []
    for round_number in range(1, 5):
        ids = [f'{round_number}-{i}' for i in range(10)]
        source.extend([{'event': 'selection', 'ids': ids, 'prediction_ranges':
                        {i: {'lower': 0., 'upper': 1.} for i in ids}},
                       {'event': 'reveal', 'measurements': {i: 2. if round_number == 2 else 0.5 for i in ids}}])
        replay.append({'event': 'reveal_reference', 'round': round_number, 'identifiers': ids})
        for kind in ('support_shift', 'coverage'):
            replay.append({'event': 'warning', 'round': round_number, 'type': kind,
                           'stage': 'post_reveal', 'status': 'triggered'})
    return source, replay


class FollowupTests(unittest.TestCase):
    def test_disjoint_followup_and_censoring(self):
        source, replay = records()
        rows = evaluate(source, replay)
        self.assertEqual(rows[0]['later_covered'], 20)
        self.assertTrue(rows[0]['later_low_coverage'])
        self.assertIsNone(rows[2]['later_low_coverage'])
        summary = summarize([row for row in rows if row['warning'] == 'coverage'])
        self.assertEqual(summary['true_alarm'], 1)
        self.assertEqual(summary['followup_unavailable'], 3)
        self.assertEqual(summary['precision'], 1)

    def test_undefined_rates_and_unavailable(self):
        summary = summarize([{'status': 'unavailable', 'later_low_coverage': None},
                             {'status': 'not_triggered', 'later_low_coverage': False}])
        self.assertIsNone(summary['precision'])
        self.assertIsNone(summary['recall'])
        self.assertEqual(summary['warning_unavailable'], 1)

    def test_later_coverage_boundary(self):
        source, replay = records()
        for identifier in list(source[3]['measurements'])[:6]:
            source[3]['measurements'][identifier] = 0.5
        self.assertFalse(evaluate(source, replay)[0]['later_low_coverage'])
        source[3]['measurements'][next(iter(source[3]['measurements']))] = 2.
        self.assertTrue(evaluate(source, replay)[0]['later_low_coverage'])

    def test_rejects_altered_records(self):
        source, replay = records()
        source[1]['measurements'].pop(next(iter(source[1]['measurements'])))
        with self.assertRaises(ValueError):
            evaluate(source, replay)
        source, replay = records()
        replay[0]['identifiers'] = ['wrong']
        with self.assertRaises(ValueError):
            evaluate(source, replay)
        source, replay = records()
        replay[1]['round'] = 2
        with self.assertRaises(ValueError):
            evaluate(source, replay)


if __name__ == '__main__':
    unittest.main()
