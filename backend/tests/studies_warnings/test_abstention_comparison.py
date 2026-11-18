import csv
import gzip
import io
import itertools
import json
import sys
import tempfile
import unittest
from collections import Counter
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import numpy as np

from app.features.representations import sequence_id
from app.datasets.flip2 import load_flip2
from scripts.repair import compare_abstention
from scripts.repair.audit_abstention import audit_run, check_action_order, check_stopping


class AbstentionComparisonTests(unittest.TestCase):
    def test_audit_rejects_missing_or_reordered_actions(self):
        actions = [{'warning': 'support_shift'}, {'warning': 'coverage'}]
        check_action_order(actions, ['support_shift', 'coverage'], True, 0)
        check_action_order(actions[:1], ['support_shift', 'coverage'], True, 2)
        with self.assertRaisesRegex(ValueError, 'Missing or reordered'):
            check_action_order(actions[:1], ['support_shift', 'coverage'], False, 2)
        with self.assertRaisesRegex(ValueError, 'Missing or reordered'):
            check_action_order(list(reversed(actions)), ['support_shift', 'coverage'], True, 2)

    def test_synthetic_evidence_gate_comparison(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            data, reference, output = root / 'data.csv', root / 'ref.fasta', root / 'runs'
            reference.write_text('>ref\nAAA\n')
            sequences = ['A' + a + b for a, b in itertools.islice(
                itertools.product('ACDEFGHIKLMNPQRSTVWY', repeat=2), 120)]
            with data.open('w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['sequence', 'target', 'set', 'validation'])
                writer.writerows((s, i / 100, 'train' if i < 110 else 'test', 'False')
                                 for i, s in enumerate(sequences))
            vectors = {sequence_id(s): np.asarray([i / 120, (i % 19) / 19], dtype=np.float32)
                       for i, s in enumerate(sequences)}
            seqs, scores, train, _, _ = load_flip2(data, reference, 4)
            for comparison, seed, expected_count in (('evidence', 81, 2), ('repair-terms', 91, 4),
                                                     ('universal', 101, 2), ('retention', 111, 2), ('later-rollback', 161, 2),
                                                     ('reactive-calibration', 171, 2)):
                output = root / comparison
                with patch.object(compare_abstention, 'DATA', data), patch.object(compare_abstention, 'REFERENCE', reference), \
                     patch.object(compare_abstention, 'EVIDENCE_SEEDS', (81,)), patch.object(compare_abstention, 'TERM_SEEDS', (91,)), \
                     patch.object(compare_abstention, 'UNIVERSAL_SEEDS', (101,)), \
                     patch.object(compare_abstention, 'RETENTION_SEEDS', (111,)), \
                     patch.object(compare_abstention, 'ROLLBACK_SEEDS', (161,)), \
                     patch.object(compare_abstention, 'CALIBRATION_SEEDS', (171,)), \
                     patch('app.datasets.amylase.DATA', data), patch('app.datasets.amylase.REFERENCE', reference), \
                     patch('app.experiments.prediction_pilot.load_verified_representations', return_value=vectors), \
                     patch.object(sys, 'argv', ['compare_abstention.py', str(output), '--comparison', comparison]), \
                     redirect_stdout(io.StringIO()):
                    compare_abstention.main()
                manifest = json.loads((output / 'manifest.json').read_text())
                with (output / 'summary.csv').open(newline='') as file:
                    rows = list(csv.DictReader(file))
                self.assertEqual([row['status'] for row in rows], ['completed'] * expected_count)
                starts = []
                for row in rows:
                    method = row['method']
                    raw = gzip.decompress((output / f'seed_{seed}' / method / 'run.jsonl.gz').read_bytes())
                    events = [json.loads(line) for line in raw.splitlines()]
                    self.assertEqual(events[1]['settings']['bypass_evidence_gate'], method == 'bypass')
                    self.assertEqual(events[1]['settings']['universal_penalty'], method == 'universal')
                    self.assertEqual(events[1]['settings']['apply_last_rejected'], method == 'no_retention')
                    self.assertEqual(events[1]['settings']['rollback_monitor'], method == 'rollback')
                    self.assertEqual(events[1]['settings']['reactive_calibration'], method == 'reactive')
                    expected = [compare_abstention.REMOVED_TERMS[method]] if method in compare_abstention.REMOVED_TERMS else []
                    self.assertEqual(events[1]['settings']['disabled_repair_terms'], expected)
                    audit_method = 'fixed' if comparison == 'reactive-calibration' else 'direct'
                    starts.append(audit_run(events, seed, audit_method, seqs, scores, train, manifest, row, Counter(),
                                            bypass_evidence_gate=method == 'bypass',
                                            apply_last_rejected=method == 'no_retention',
                                            rollback_monitor=method == 'rollback',
                                            reactive_calibration=method == 'reactive'))
                    check_stopping(events, True)
                self.assertTrue(all(start == starts[0] for start in starts))

    def test_audit_checks_stopping_and_counts(self):
        actions = [{'status': 'retained', 'consecutive_failures': 1},
                   {'status': 'retained', 'consecutive_failures': 2}]
        events = [{'event': 'method', 'settings': {'repair_actions': actions, 'consecutive_failures': 2}},
                  {'event': 'stop', 'stop_reason': 'failed_repairs'}]
        check_stopping(events, True)
        with self.assertRaisesRegex(ValueError, 'Unexpected failed-repair stop'):
            check_stopping(events, False)
        with self.assertRaisesRegex(ValueError, 'Missing required stop'):
            check_stopping(events[:1], True)
        check_stopping(events[:1], False)

    def test_synthetic_matched_run(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            data, reference, output = root / 'data.csv', root / 'ref.fasta', root / 'runs'
            reference.write_text('>ref\nAAA\n')
            sequences = ['A' + a + b for a, b in itertools.islice(
                itertools.product('ACDEFGHIKLMNPQRSTVWY', repeat=2), 120)]
            with data.open('w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['sequence', 'target', 'set', 'validation'])
                writer.writerows((s, i / 100, 'train' if i < 110 else 'test', 'False')
                                 for i, s in enumerate(sequences))
            vectors = {sequence_id(s): np.asarray([i / 120, (i % 19) / 19], dtype=np.float32)
                       for i, s in enumerate(sequences)}
            with patch.object(compare_abstention, 'DATA', data), patch.object(compare_abstention, 'REFERENCE', reference), \
                 patch.object(compare_abstention, 'SEEDS', (71,)), patch('app.datasets.amylase.DATA', data), \
                 patch('app.datasets.amylase.REFERENCE', reference), \
                 patch('app.experiments.prediction_pilot.load_verified_representations', return_value=vectors), \
                 patch.object(sys, 'argv', ['compare_abstention.py', str(output)]), redirect_stdout(io.StringIO()):
                compare_abstention.main()
            with (output / 'summary.csv').open(newline='') as file:
                rows = list(csv.DictReader(file))
            self.assertEqual([row['status'] for row in rows], ['completed', 'completed'])
            events = []
            for method in ('normal', 'continue'):
                raw = gzip.decompress((output / 'seed_71' / method / 'run.jsonl.gz').read_bytes())
                events.append([json.loads(line) for line in raw.splitlines()])
            self.assertEqual(events[0][0]['initial'], events[1][0]['initial'])
            for record, normal in zip(events, (True, False)):
                self.assertEqual(record[1]['settings']['stop_on_failed_repairs'], normal)
                check_stopping(record, normal)


if __name__ == '__main__':
    unittest.main()
