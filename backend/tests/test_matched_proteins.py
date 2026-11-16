import copy
import csv
import gzip
import itertools
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np

from app.features.representations import sequence_id
from app.llm.goal_compiler import DEFAULT_SPEC

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
from run_matched_proteins import main


class MatchedProteinTests(unittest.TestCase):
    def test_synthetic_comparison_and_resume(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            data, reference, spec, output = (root / name for name in ('data.csv', 'reference.fasta', 'spec.json', 'runs'))
            reference.write_text('>synthetic\nAAA\n')
            sequences = ['A' + a + b for a, b in itertools.islice(itertools.product('ACDEFGHIKLMNPQRSTVWY', repeat=2), 120)]
            with data.open('w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['sequence', 'target', 'set', 'validation'])
                writer.writerows((sequence, index / 100, 'train' if index < 110 else 'test', 'False')
                                 for index, sequence in enumerate(sequences))
            spec.write_text(json.dumps(DEFAULT_SPEC))
            vectors = {sequence_id(sequence): np.asarray([i / 120, (i % 19) / 19], dtype=np.float32)
                       for i, sequence in enumerate(sequences)}
            argv = ['run_matched_proteins.py', str(output), '--dataset', 'ired', '--seeds', '7',
                    '--methods', 'random', 'greedy', '--specification', str(spec)]
            with patch('app.datasets.ired.DATA', data), patch('app.datasets.ired.REFERENCE', reference), \
                 patch('app.features.ired_representations.load_verified_representations', return_value=vectors), \
                 patch.object(sys, 'argv', argv):
                main()
                manifest = json.loads((output / 'manifest.json').read_text())
                self.assertEqual(manifest['initial_pool'], 'eligible')
                records = []
                for method in ('random', 'greedy'):
                    path = output / 'seed_07' / method
                    self.assertEqual(json.loads((path / 'status.json').read_text())['status'], 'completed')
                    records.append([json.loads(line) for line in gzip.decompress((path / 'run.jsonl.gz').read_bytes()).splitlines()])
                self.assertEqual(records[0][0]['initial'], records[1][0]['initial'])
                self.assertEqual(records[0][0]['initial_pool'], 'eligible')
                with patch.object(sys, 'argv', argv + ['--resume']):
                    main()
                changed = copy.deepcopy(DEFAULT_SPEC)
                changed['terms']['uncertainty_penalty']['weight'] = 0.75
                spec.write_text(json.dumps(changed))
                with patch.object(sys, 'argv', argv + ['--resume']), self.assertRaisesRegex(ValueError, 'changed inputs'):
                    main()
                spec.write_text(json.dumps(DEFAULT_SPEC))
                path = output / 'seed_07' / 'random' / 'run.jsonl.gz'
                path.write_bytes(path.read_bytes() + b'altered')
                with patch.object(sys, 'argv', argv + ['--resume']), self.assertRaisesRegex(ValueError, 'fingerprint mismatch'):
                    main()
                failed_output = root / 'failed'
                failed_argv = ['run_matched_proteins.py', str(failed_output), '--dataset', 'ired', '--seeds', '7',
                               '--methods', 'random', '--specification', str(spec)]
                with patch.object(sys, 'argv', failed_argv), patch('run_matched_proteins.run_one', side_effect=RuntimeError), \
                     self.assertRaises(SystemExit):
                    main()
                status = json.loads((failed_output / 'seed_07/random/status.json').read_text())
                self.assertEqual((status['status'], status['error_type']), ('failed', 'RuntimeError'))
                with patch.object(sys, 'argv', failed_argv + ['--resume']), \
                     patch('run_matched_proteins.run_one') as retry, self.assertRaises(SystemExit):
                    main()
                retry.assert_not_called()


if __name__ == '__main__':
    unittest.main()
