import gzip
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.analysis.repeated_evaluation import evaluate_repeated
from app.experiments.repeated_runs import METHODS, run_one
from app.features.amylase_representations import CACHE_SHA256
from app.llm.goal_compiler import DEFAULT_SPEC


class RepeatedTests(unittest.TestCase):
    def test_method_dispatch_and_advisor_boundary(self):
        with patch('app.experiments.repeated_runs.run_pilot') as pilot, \
             patch('app.experiments.repeated_runs.run_random') as random:
            for method in METHODS:
                run_one('path', 21, method, DEFAULT_SPEC, advisor=lambda *_: None, model='model')
        self.assertEqual(random.call_count, 1)
        self.assertEqual(pilot.call_count, 8)
        calls = [call.kwargs for call in pilot.call_args_list]
        self.assertTrue(all(call['role_seed'] == 2021 and call['member_seed'] == 3021 for call in calls))
        self.assertEqual(sum(call.get('repair', False) for call in calls), 2)
        self.assertEqual(sum('repair_advisor' in call for call in calls), 1)

    def test_evaluation_matches_inputs_and_rejects_tampering(self):
        scores = {f'i{i:03}': float(i) for i in range(101)}
        initial = {f'i{i:03}': float(i) for i in range(100)}
        start = {'event': 'start', 'seed': 21, 'initial_count': 100, 'budget': 100,
                 'batch_size': 10, 'max_mutations': 4, 'data_sha256': 'data',
                 'reference_sha256': 'ref', 'initial': initial, 'stop_reason': None}
        settings = {'dataset': 'amylase', 'cache_sha256': CACHE_SHA256, 'role_seed': 2021,
                    'member_seed': 3021, 'reserved_ids': list(initial)[:20], 'penalties': [0.1, 1, 10, 100],
                    'folds': 5, 'cv_seed': 21, 'cv_scoring': 'neg_mean_squared_error', 'member_count': 5,
                    'spread_ddof': 0, 'nominal_coverage': 0.9, 'interval': 'x', 'reward_spec': None,
                    'repair': False, 'acquisition': None, 'local_search': None}
        events = [start, {'event': 'method', 'settings': settings},
                  {'event': 'selection', 'ids': ['i100']},
                  {'event': 'reveal', 'measurements': {'i100': 100.0}, 'remaining': 99,
                   'stop_reason': 'no_candidates'}]
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = root / 'seed_21/greedy'
            path.mkdir(parents=True)
            raw = ''.join(json.dumps(event) + '\n' for event in events).encode()
            blob = gzip.compress(raw, mtime=0)
            (path / 'run.jsonl.gz').write_bytes(blob)
            (path / 'status.json').write_text(json.dumps({'status': 'completed', 'elapsed_seconds': 1,
                'uncompressed_sha256': hashlib.sha256(raw).hexdigest(), 'gzip_sha256': hashlib.sha256(blob).hexdigest()}))
            rows, curves = evaluate_repeated(root, [21], ['greedy'], scores, set(initial), 'data', 'ref', DEFAULT_SPEC)
            self.assertEqual(rows[0]['stop_reason'], 'no_candidates')
            self.assertEqual(curves[-1]['new_measurements'], 1)
            (path / 'run.jsonl.gz').write_bytes(blob + b'wrong')
            with self.assertRaises(ValueError):
                evaluate_repeated(root, [21], ['greedy'], scores, set(initial), 'data', 'ref', DEFAULT_SPEC)
