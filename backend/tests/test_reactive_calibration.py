import copy
import csv
import itertools
import sys
from collections import Counter
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np

from app.datasets.amylase import load_amylase
from app.experiments.evaluation import evaluate
from app.analysis.recovery import summarize_recovery
from app.experiments.calibration_policy import recent_calibration
from app.experiments.prediction_pilot import run_pilot
from app.features.representations import sequence_id
from app.llm.goal_compiler import DEFAULT_SPEC

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
from audit_development_repairs import audit_run


class ReactiveCalibrationTest(unittest.TestCase):
    def test_recent_revealed_only_and_invalid_history(self):
        history = [(f'i{i:02}', i % 2 == 0) for i in range(30)]
        self.assertEqual(recent_calibration(history, [x[0] for x in history]),
                         sorted(x[0] for x in history[-20:]))
        for bad, known in ((history[:19], [x[0] for x in history]),
                           (history + [history[-1]], [x[0] for x in history]),
                           (history, [x[0] for x in history[:-1]]),
                           (history[:-1] + [('last', 1)], [x[0] for x in history] + ['last'])):
            with self.subTest(bad=bad[-1]), self.assertRaises(ValueError):
                recent_calibration(bad, known)

    def test_invalid_scope(self):
        for kwargs in ({'reactive_calibration': True},
                       {'reactive_calibration': True, 'reward_spec': DEFAULT_SPEC, 'dataset': 'ired'},
                       {'reactive_calibration': True, 'reward_spec': DEFAULT_SPEC, 'repair': True,
                        'rollback_monitor': True}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                run_pilot('unused', **kwargs)

    def test_warning_updates_only_next_fit(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            data, reference = root / 'data.csv', root / 'reference.fasta'
            reference.write_text('>synthetic\nAAA\n')
            sequences = ['A' + a + b for a, b in itertools.islice(
                itertools.product('ACDEFGHIKLMNPQRSTVWY', repeat=2), 160)]
            with data.open('w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['sequence', 'target', 'set', 'validation'])
                writer.writerows((s, (i % 17) ** 2 / 10, 'train' if i < 120 else 'test', 'False')
                                 for i, s in enumerate(sequences))
            vectors = {sequence_id(s): np.asarray([i / 160, (i % 19) / 19], dtype=np.float32)
                       for i, s in enumerate(sequences)}
            with patch('app.datasets.amylase.DATA', data), patch('app.datasets.amylase.REFERENCE', reference), \
                 patch('app.experiments.prediction_pilot.load_verified_representations', return_value=vectors), \
                 patch('app.experiments.prediction_pilot.interval_radius', return_value=0.):
                run_pilot(root / 'adaptive', seed=7, role_seed=2007, member_seed=3007,
                          reward_spec=copy.deepcopy(DEFAULT_SPEC), reactive_calibration=True)
                run_pilot(root / 'original', seed=7, role_seed=2007, member_seed=3007,
                          reward_spec=copy.deepcopy(DEFAULT_SPEC))
                with patch('app.experiments.prediction_pilot.handle_warnings',
                           side_effect=lambda spec, *args, **kwargs: (spec, 0, [], False)):
                    run_pilot(root / 'repair', seed=7, role_seed=2007, member_seed=3007,
                              reward_spec=copy.deepcopy(DEFAULT_SPEC), repair=True, reactive_calibration=True)
                calls = []
                def stop_after_three(spec, *args, **kwargs):
                    calls.append(1)
                    return spec, 2 if len(calls) == 3 else 0, [], len(calls) == 3
                with patch('app.experiments.prediction_pilot.handle_warnings', side_effect=stop_after_three):
                    run_pilot(root / 'stopped', seed=7, role_seed=2007, member_seed=3007,
                              reward_spec=copy.deepcopy(DEFAULT_SPEC), repair=True, reactive_calibration=True)
            events = [json.loads(line) for line in (root / 'adaptive/run.jsonl').read_text().splitlines()]
            initial = next(e['settings']['reserved_ids'] for e in events if e['event'] == 'method')
            observed, current, round_number, updates = [], initial, 0, 0
            for event in events:
                if event['event'] == 'method' and 'member_seeds' in event['settings']:
                    round_number += 1
                    settings = event['settings']
                    self.assertEqual(settings['calibration_ids'], current)
                    self.assertFalse(set(current) & set(settings['fitting_ids']))
                elif event['event'] == 'reveal':
                    observed.extend(event['measurements'])
                elif event['event'] == 'method' and 'calibration_update' in event['settings']:
                    update = event['settings']['calibration_update']
                    self.assertGreaterEqual(len(observed), 30)
                    self.assertEqual(update['previous_ids'], current)
                    self.assertEqual(update['new_ids'], sorted(observed[-20:]))
                    self.assertEqual(update['active_from_round'], round_number + 1)
                    current = update['new_ids']
                    updates += 1
            self.assertGreater(updates, 0)
            seqs, scores, train, data_hash, ref_hash = load_amylase(data, reference, 4)
            evaluation = evaluate(events, scores, set(train), data_hash, ref_hash)
            row = {'status': 'completed', **evaluation['curve'][-1],
                   'stop_reason': evaluation['stop_reason'], 'covered': evaluation['covered'],
                   'range_count': evaluation['range_count'], 'mean_range_width': evaluation['mean_range_width']}
            row['found_top_one_percent'] = str(row['found_top_one_percent'])
            manifest = {'data_sha256': data_hash, 'reference_sha256': ref_hash}
            summarize_recovery(events)
            audit_run(events, 7, 'fixed', seqs, scores, train, manifest, row, Counter(), reactive_calibration=True)
            altered = copy.deepcopy(events)
            update = next(e['settings']['calibration_update'] for e in altered
                          if e['event'] == 'method' and 'calibration_update' in e['settings'])
            update['new_ids'].reverse()
            with self.assertRaisesRegex(ValueError, 'Calibration update mismatch'):
                audit_run(altered, 7, 'fixed', seqs, scores, train, manifest, row, Counter(), reactive_calibration=True)
            baseline = [json.loads(line) for line in (root / 'original/run.jsonl').read_text().splitlines()]
            self.assertFalse(any('calibration_update' in e.get('settings', {}) for e in baseline))
            repair = [json.loads(line) for line in (root / 'repair/run.jsonl').read_text().splitlines()]
            update_index = next(i for i, e in enumerate(repair) if 'calibration_update' in e.get('settings', {}))
            self.assertIn('repair_actions', repair[update_index - 1]['settings'])
            stopped = [json.loads(line) for line in (root / 'stopped/run.jsonl').read_text().splitlines()]
            self.assertEqual(next(e for e in stopped if e['event'] == 'stop')['stop_reason'], 'failed_repairs')
            self.assertFalse(any('calibration_update' in e.get('settings', {}) for e in stopped))


if __name__ == '__main__':
    unittest.main()
