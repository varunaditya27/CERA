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

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
import compare_abstention
from audit_abstention import audit_run, check_stopping


class AbstentionComparisonTests(unittest.TestCase):
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
            with patch.object(compare_abstention, 'DATA', data), patch.object(compare_abstention, 'REFERENCE', reference), \
                 patch.object(compare_abstention, 'EVIDENCE_SEEDS', (81,)), patch('app.datasets.amylase.DATA', data), \
                 patch('app.datasets.amylase.REFERENCE', reference), \
                 patch('app.experiments.prediction_pilot.load_verified_representations', return_value=vectors), \
                 patch.object(sys, 'argv', ['compare_abstention.py', str(output), '--comparison', 'evidence']), \
                 redirect_stdout(io.StringIO()):
                compare_abstention.main()
            manifest = json.loads((output / 'manifest.json').read_text())
            with (output / 'summary.csv').open(newline='') as file:
                rows = list(csv.DictReader(file))
            self.assertEqual([row['status'] for row in rows], ['completed', 'completed'])
            seqs, scores, train, _, _ = load_flip2(data, reference, 4)
            starts = []
            for row in rows:
                method = row['method']
                raw = gzip.decompress((output / 'seed_81' / method / 'run.jsonl.gz').read_bytes())
                events = [json.loads(line) for line in raw.splitlines()]
                self.assertEqual(events[1]['settings']['bypass_evidence_gate'], method == 'bypass')
                starts.append(audit_run(events, 81, 'direct', seqs, scores, train, manifest, row, Counter(),
                                        bypass_evidence_gate=method == 'bypass'))
                check_stopping(events, True)
            self.assertEqual(starts[0], starts[1])

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
