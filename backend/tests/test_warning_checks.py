import csv
import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

from app.warning_checks import (constraint_warning, coverage_warning, disagreement_warning,
                                distance_snapshot, diversity_warning, support_warning)
from app.experiment import Experiment


class WarningTests(unittest.TestCase):
    def test_constraint_boundaries_and_invalid_batches(self):
        candidates = {'a': 'CCCCA', 'b': 'CCCCC', 'c': 'AACAA'}
        self.assertEqual(constraint_warning(['a'], candidates, 'AAAAA', 1)['status'], 'not_triggered')
        for ids in (['b'], ['c', 'unknown'], ['c', 'c'], ['unknown'], ['c', 'a']):
            with self.subTest(ids=ids):
                self.assertEqual(constraint_warning(ids, candidates, 'AAAAA', 1)['status'], 'triggered')
        duplicate = constraint_warning(['c', 'c'], candidates, 'AAAAA', 2)
        self.assertEqual(duplicate['reason'], 'duplicate')
        with self.assertRaises(ValueError):
            constraint_warning(['bad'], {'bad': 'AA'}, 'AAAAA', 1)

    def test_distance_snapshot_excludes_self_and_handles_duplicates(self):
        vectors = {'a': [0.], 'b': [2.], 'c': [2.], 'x': [5.]}
        snapshot = distance_snapshot(['a', 'b', 'c'], ['x'], vectors)
        self.assertEqual(snapshot['threshold'], 2.)
        self.assertEqual(snapshot['distances']['x'], 3.)
        unavailable = distance_snapshot(['a'], ['x'], vectors)
        self.assertIsNone(unavailable['threshold'])
        with self.assertRaises(ValueError):
            distance_snapshot(['a', 'b'], ['a'], vectors)
        with self.assertRaises(ValueError):
            distance_snapshot(['a', 'b'], ['x'], {**vectors, 'x': [float('nan')]})
        with self.assertRaises(ValueError):
            distance_snapshot(['a'], ['x'], {**vectors, 'x': [float('nan')]})

    def test_support_joint_rule_and_boundaries(self):
        batch = ['a', 'b', 'c', 'd', 'e']
        snapshot = {'batch_ids': batch, 'known_ids': ['k1', 'k2'], 'threshold': 2.,
                    'distances': {'a': 3., 'b': 3., 'c': 3., 'd': 2., 'e': 3.}}
        ranges = {key: {'lower': 0., 'upper': 1.} for key in batch}
        scores = {'a': 2., 'b': 2., 'c': 2., 'd': 2., 'e': 1.}
        self.assertEqual(support_warning(snapshot, ranges, scores)['status'], 'triggered')
        scores['c'] = 1.
        warning = support_warning(snapshot, ranges, scores)
        self.assertEqual(warning['status'], 'not_triggered')
        self.assertEqual(warning['value'], 2)
        self.assertEqual(support_warning(snapshot, ranges, dict.fromkeys(batch, 1.))['value'], 0)
        unavailable = {'batch_ids': batch, 'known_ids': ['k1'], 'threshold': None, 'distances': {}}
        self.assertEqual(support_warning(unavailable, ranges, scores)['status'], 'unavailable')
        with self.assertRaises(ValueError):
            support_warning(snapshot, ranges, {'a': float('nan')})

    def test_coverage_window_and_boundaries(self):
        history = [(str(i), i < 22) for i in range(30)]
        self.assertEqual(coverage_warning(history[:29])['status'], 'unavailable')
        self.assertEqual(coverage_warning(history)['status'], 'triggered')
        history[22] = ('22', True)
        self.assertEqual(coverage_warning(history)['status'], 'not_triggered')
        extended = [('old', False)] + [(str(i), True) for i in range(30)]
        self.assertEqual(coverage_warning(extended)['value'], 1.)
        with self.assertRaises(ValueError):
            coverage_warning([('a', 1)])

    def test_disagreement_rankings_ties_and_unavailable(self):
        means = {'a': 3., 'b': 2., 'c': 1.}
        same = {'a': [3.] * 5, 'b': [2.] * 5, 'c': [1.] * 5}
        self.assertEqual(disagreement_warning(means, same)['status'], 'not_triggered')
        opposed = {'a': [3., 3., 3., 1., 1.], 'b': [2.] * 5, 'c': [1., 1., 1., 3., 3.]}
        self.assertEqual(disagreement_warning(means, opposed)['status'], 'triggered')
        constant = {'a': [1., 3., 3., 3., 3.], 'b': [1., 2., 2., 2., 2.], 'c': [1., 1., 1., 1., 1.]}
        self.assertEqual(disagreement_warning(means, constant)['status'], 'unavailable')
        self.assertEqual(disagreement_warning({'a': 1.}, {'a': [1.] * 5})['status'], 'unavailable')
        tied_means = {'b': 1., 'a': 1., 'c': 0.}
        tied_members = {'a': [2.] * 5, 'b': [2.] * 5, 'c': [1.] * 5}
        self.assertEqual(disagreement_warning(tied_means, tied_members)['identifiers'], ['a', 'b', 'c'])
        columns = ((0, 1, 2, 3), (0, 1, 2, 3), (0, 1, 2, 3), (0, 1, 3, 2), (1, 3, 0, 2))
        boundary_means = {str(i): float(4 - i) for i in range(4)}
        boundary_members = {str(i): [column[i] for column in columns] for i in range(4)}
        boundary = disagreement_warning(boundary_means, boundary_members)
        self.assertEqual(boundary['value'], 0.5)
        self.assertEqual(boundary['status'], 'not_triggered')
        with self.assertRaises(ValueError):
            disagreement_warning(means, {'a': [float('nan')] * 5})
        invalid = {identifier: list(values) for identifier, values in same.items()}
        invalid['a'][0] = float('nan')
        with self.assertRaises(ValueError):
            disagreement_warning(means, invalid)

    def test_disagreement_uses_only_top_hundred(self):
        means = {str(i): float(i) for i in range(101)}
        top = sorted(means, key=lambda i: (-means[i], i))[:100]
        members = {i: [means[i]] * 5 for i in top}
        warning = disagreement_warning(means, members)
        self.assertEqual(len(warning['identifiers']), 100)
        self.assertNotIn('0', warning['identifiers'])

    def test_diversity_boundaries(self):
        self.assertEqual(diversity_warning({'a': 'AAAA', 'b': 'AAAC'})['status'], 'triggered')
        self.assertEqual(diversity_warning({'a': 'AAAA', 'b': 'AACC'})['status'], 'not_triggered')
        self.assertEqual(diversity_warning({'a': 'AAAA', 'b': 'ACCC'})['status'], 'not_triggered')
        self.assertEqual(diversity_warning({'a': 'AAAA'})['status'], 'unavailable')
        self.assertAlmostEqual(diversity_warning({'a': 'AAAA', 'b': 'AAAC', 'c': 'AACC'})['value'], 4 / 3)
        for batch in ({'a': 'AAAA', 'b': 'AA'}, {'a': 'AAAA', 'b': 'AAAA'}, {}):
            with self.subTest(batch=batch), self.assertRaises(ValueError):
                diversity_warning(batch)

    def test_warnings_are_recorded_and_invalid_reveal_stays_atomic(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'ref').write_text('>ref\nAAAA\n')
            with (root / 'data').open('w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['sequence', 'target', 'set', 'validation'])
                writer.writerows([('AAAA', 1, 'train', 'False'), ('CAAA', 2, 'test', 'False')])
            run = Experiment(root / 'data', root / 'ref', root / 'log', 1, initial_count=1, budget=1)
            self.addCleanup(run.close)
            candidate = next(iter(run.candidates))
            warning = constraint_warning([candidate, 'unknown'], run.candidates, 'AAAA', run.remaining)
            run.record_warning(1, warning)
            with self.assertRaises(ValueError):
                run.reveal([candidate, 'unknown'])
            self.assertEqual(run.remaining, 1)
            events = [json.loads(line) for line in (root / 'log').read_text().splitlines()]
            self.assertEqual([event['event'] for event in events], ['start', 'warning'])
            self.assertEqual(events[-1]['round'], 1)
            self.assertEqual(events[-1]['status'], 'triggered')

    def test_support_warning_reconstructs_from_saved_pre_reveal_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'ref').write_text('>ref\nAAAA\n')
            with (root / 'data').open('w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['sequence', 'target', 'set', 'validation'])
                writer.writerows([('AAAA', 0, 'train', 'False'), ('CAAA', 0, 'train', 'False'),
                                  ('ACAA', 3, 'test', 'False'), ('AACA', 4, 'test', 'False'),
                                  ('AAAC', 5, 'test', 'False')])
            run = Experiment(root / 'data', root / 'ref', root / 'log', 1, initial_count=2, budget=3)
            self.addCleanup(run.close)
            known = sorted(run.revealed)
            chosen = sorted(run.candidates)
            vectors = {known[0]: [0.], known[1]: [2.], chosen[0]: [5.], chosen[1]: [6.], chosen[2]: [7.]}
            snapshot = distance_snapshot(known, chosen, vectors)
            ranges = {i: {'mean': 0.5, 'spread': 0., 'lower': 0., 'upper': 1.} for i in chosen}
            run.record_settings({'distance_snapshot': snapshot})
            measured = run.reveal(chosen, prediction_ranges=ranges)
            run.record_warning(1, support_warning(snapshot, ranges, measured))
            events = [json.loads(line) for line in (root / 'log').read_text().splitlines()]
            self.assertEqual([e['event'] for e in events], ['start', 'method', 'selection', 'reveal', 'warning'])
            reconstructed = support_warning(events[1]['settings']['distance_snapshot'],
                                            events[2]['prediction_ranges'], events[3]['measurements'])
            self.assertEqual(reconstructed['status'], 'triggered')
            for key, value in reconstructed.items():
                self.assertEqual(events[4][key], value)


if __name__ == '__main__':
    unittest.main()
