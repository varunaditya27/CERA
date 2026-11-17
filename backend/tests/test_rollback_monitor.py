import copy
import csv
import itertools
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np

from app.experiments.prediction_pilot import run_pilot
from app.analysis.rollback_audit import audit_rollback_events
from app.features.representations import sequence_id
from app.llm.goal_compiler import DEFAULT_SPEC
from app.rewards.rollback_monitor import RollbackMonitor


def changed(spec, value):
    result = copy.deepcopy(spec)
    result['terms']['uncertainty_penalty']['weight'] = value
    return result


def observations(start, count, covered):
    return [(f'i{i}', i - start < covered) for i in range(start, start + count)]


class RollbackMonitorTest(unittest.TestCase):
    def test_boundary_and_incomplete_followup(self):
        for covered, expected in ((22, 'rolled_back'), (23, 'retained')):
            with self.subTest(covered=covered):
                monitor = RollbackMonitor()
                prior, current = copy.deepcopy(DEFAULT_SPEC), changed(DEFAULT_SPEC, .75)
                monitor.register(prior, current, 1)
                result, events = monitor.observe(current, 2, observations(0, 20, min(covered, 20)))
                self.assertEqual(events[0]['status'], 'pending')
                self.assertEqual(result, current)
                result, events = monitor.observe(current, 3, observations(20, 10, covered - 20))
                self.assertEqual(events[0]['status'], expected)
                self.assertEqual(result, prior if expected == 'rolled_back' else current)
                self.assertEqual(monitor.finish(), [])
        monitor = RollbackMonitor()
        monitor.register(DEFAULT_SPEC, changed(DEFAULT_SPEC, .75), 1)
        monitor.observe(changed(DEFAULT_SPEC, .75), 2, observations(0, 10, 10))
        self.assertEqual(monitor.finish()[0]['status'], 'insufficient_followup')
        self.assertEqual(monitor.finish(), [])

    def test_supersession_and_immutable_versions(self):
        monitor = RollbackMonitor()
        original = copy.deepcopy(DEFAULT_SPEC)
        first, second = changed(original, .75), changed(original, 1.0)
        monitor.register(original, first, 1)
        monitor.observe(first, 2, observations(0, 10, 0))
        events = monitor.register(first, second, 2)
        self.assertEqual([e['status'] for e in events], ['superseded', 'monitoring'])
        first['terms']['uncertainty_penalty']['weight'] = 2
        restored, events = monitor.observe(second, 3, observations(10, 30, 0))
        self.assertEqual(restored['terms']['uncertainty_penalty']['weight'], .75)
        self.assertEqual(events[0]['covered'], 0)
        self.assertEqual(len(events[0]['observations']), 30)

    def test_rejects_invalid_lineage_observations_and_constraints(self):
        monitor = RollbackMonitor()
        previous, current = copy.deepcopy(DEFAULT_SPEC), changed(DEFAULT_SPEC, .75)
        altered = copy.deepcopy(current)
        altered['hard_constraints']['max_mutations'] = 3
        with self.assertRaises(ValueError):
            monitor.register(previous, altered, 1)
        monitor.register(previous, current, 1)
        for rows in ([], [('x', 1)], [('x', True), ('x', False)]):
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                monitor.observe(current, 2, rows)
        with self.assertRaises(ValueError):
            monitor.observe(previous, 2, [('x', True)])
        monitor.observe(current, 2, [('x', True)])
        with self.assertRaises(ValueError):
            monitor.observe(current, 2, [('y', True)])
        with self.assertRaises(ValueError):
            monitor.observe(current, 3, [('x', False)])
        with self.assertRaises(ValueError):
            monitor.register(previous, changed(previous, 1.0), 3)

    def test_end_to_end_monitor_rolls_back_after_later_measurements(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            data, reference = root / 'data.csv', root / 'ref.fasta'
            reference.write_text('>synthetic\nAAA\n')
            sequences = ['A' + a + b for a, b in itertools.islice(
                itertools.product('ACDEFGHIKLMNPQRSTVWY', repeat=2), 160)]
            with data.open('w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['sequence', 'target', 'set', 'validation'])
                writer.writerows((seq, i / 100, 'train' if i < 120 else 'test', 'False')
                                 for i, seq in enumerate(sequences))
            vectors = {sequence_id(seq): np.asarray([i / 160, (i % 19) / 19], dtype=np.float32)
                       for i, seq in enumerate(sequences)}
            proposed = changed(DEFAULT_SPEC, .75)
            calls = []
            def repairs(spec, *args, **kwargs):
                calls.append(copy.deepcopy(spec))
                if len(calls) == 1:
                    return proposed, 0, [{'status': 'accepted', 'specification': proposed}], False
                return spec, 0, [], False
            with patch('app.datasets.amylase.DATA', data), patch('app.datasets.amylase.REFERENCE', reference), \
                 patch('app.experiments.prediction_pilot.load_verified_representations', return_value=vectors), \
                 patch('app.experiments.prediction_pilot.interval_radius', return_value=0.), \
                 patch('app.experiments.prediction_pilot.handle_warnings', side_effect=repairs):
                run_pilot(root / 'run', seed=7, reward_spec=DEFAULT_SPEC, repair=True, rollback_monitor=True)
            events = [json.loads(line) for line in (root / 'run/run.jsonl').read_text().splitlines()]
            monitoring = [(e['settings']['round'], item) for e in events if e['event'] == 'method'
                          for item in e['settings'].get('rollback_events', [])]
            rolled = [(number, item) for number, item in monitoring if item['status'] == 'rolled_back']
            audited = audit_rollback_events(events)
            self.assertEqual(audited['rolled_back'], 1)
            altered = copy.deepcopy(events)
            next(item for e in altered if e['event'] == 'method'
                 for item in e['settings'].get('rollback_events', []) if item['status'] == 'rolled_back')['covered'] = 30
            with self.assertRaisesRegex(ValueError, 'evidence mismatch'):
                audit_rollback_events(altered)
            self.assertEqual(len(rolled), 1)
            self.assertEqual(rolled[0][0], 4)
            self.assertEqual(len(rolled[0][1]['observations']), 30)
            self.assertEqual(rolled[0][1]['previous'], DEFAULT_SPEC)
            self.assertEqual(calls[3], DEFAULT_SPEC)
            self.assertEqual(events[0]['remaining'], 100)
            self.assertEqual(next(e for e in reversed(events) if e['event'] == 'reveal')['remaining'], 40)


if __name__ == '__main__':
    unittest.main()
