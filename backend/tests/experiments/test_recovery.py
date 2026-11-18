import copy
import unittest

from app.analysis.recovery import summarize_recovery


def record(batches, budget=None):
    budget = budget if budget is not None else sum(map(len, batches))
    events = [{'event': 'start', 'initial': {}, 'budget': budget, 'batch_size': 10, 'stop_reason': None}]
    history = []
    total = 0
    for batch in batches:
        ids = [f'i{total + i}' for i in range(len(batch))]
        ranges = {i: {'lower': 0.0, 'upper': 1.0} for i in ids}
        values = {i: 0.5 if hit else 2.0 for i, hit in zip(ids, batch)}
        total += len(batch)
        events.append({'event': 'selection', 'ids': ids, 'prediction_ranges': ranges})
        events.append({'event': 'reveal', 'measurements': values, 'remaining': budget - total,
                       'stop_reason': 'budget_exhausted' if total == budget else None})
        history.extend(batch)
        status = ('unavailable' if len(history) < 30 else
                  'triggered' if sum(history[-30:]) < 22.5 else 'not_triggered')
        events.append({'event': 'warning', 'type': 'coverage', 'status': status})
    if total < budget:
        events.append({'event': 'stop', 'remaining': budget - total, 'stop_reason': 'failed_repairs'})
    return events


class RecoveryTests(unittest.TestCase):
    def test_window_boundaries_and_excludes_warning_batch(self):
        for hits, status in ((25, 'not_recovered'), (26, 'recovered'), (28, 'recovered'), (29, 'not_recovered')):
            followup = [True] * hits + [False] * (30 - hits)
            events = record([[False] * 10] * 3 + [followup[i:i + 10] for i in range(0, 30, 10)])
            result = summarize_recovery(events)
            self.assertEqual(result['status'], status)
            self.assertEqual(result['warning_after_measurements'], 30)
            self.assertEqual(result['followup_measurements'], 30)
            self.assertEqual(result['windows'][0]['covered'], hits)
            if result['recovery']:
                self.assertEqual(result['recovery']['after_measurements'], 30)
                self.assertEqual(result['recovery']['mean_width'], 1.0)

    def test_no_warning_and_insufficient_followup(self):
        self.assertEqual(summarize_recovery(record([[True] * 10] * 4))['status'], 'no_warning')
        result = summarize_recovery(record([[False] * 10] * 3 + [[True] * 10], budget=100))
        self.assertEqual(result['status'], 'insufficient_followup')
        self.assertEqual(result['followup_measurements'], 10)
        self.assertEqual(result['stop_reason'], 'failed_repairs')
        self.assertIsNone(result['recovery'])

    def test_first_recovery_after_later_sliding_window(self):
        batches = [[False] * 10] * 3 + [[False] * 10, [True] * 10, [True] * 10, [True] * 6 + [False] * 4]
        result = summarize_recovery(record(batches))
        self.assertEqual([x['covered'] for x in result['windows']], [20, 26])
        self.assertEqual(result['recovery']['after_measurements'], 40)

    def test_rejects_false_warning_missing_or_mismatched_reveal(self):
        events = record([[False] * 10] * 4)
        false_warning = copy.deepcopy(events)
        next(e for e in false_warning if e['event'] == 'warning' and e['status'] == 'triggered')['status'] = 'not_triggered'
        with self.assertRaises(ValueError):
            summarize_recovery(false_warning)
        with self.assertRaises(ValueError):
            summarize_recovery(events[:-2])
        bad_reveal = copy.deepcopy(events)
        next(e for e in bad_reveal if e['event'] == 'reveal')['measurements'].pop('i0')
        with self.assertRaises(ValueError):
            summarize_recovery(bad_reveal)
