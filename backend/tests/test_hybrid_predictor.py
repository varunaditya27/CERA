import math
import unittest

import numpy as np

from app.experiments.hybrid_predictor import fit_hybrid_group
from app.experiments.prediction_pilot import run_pilot
from app.experiments.predictor_group import fit_group, predict_members
from app.llm.goal_compiler import DEFAULT_SPEC


class HybridPredictorTest(unittest.TestCase):
    def setUp(self):
        self.fitting = [f'i{i:02}' for i in range(30)]
        self.reserved = [f'held{i}' for i in range(5)]
        self.vectors = {identifier: np.array([i / 30, (i % 7) / 7, (i % 11) / 11], dtype=np.float32)
                        for i, identifier in enumerate(self.fitting + self.reserved)}
        self.scores = {identifier: math.sin(i / 5) for i, identifier in enumerate(self.fitting)}
        self.seeds = [101, 102, 103, 104, 105]

    def test_roles_predictions_and_best_weight_restoration(self):
        models, penalty, info = fit_hybrid_group(self.vectors, self.scores, self.fitting, self.reserved,
                                                7, self.seeds, 'cpu')
        self.assertEqual(len(models), 5)
        self.assertGreater(penalty, 0)
        self.assertEqual(len(info['validation_ids']), 6)
        self.assertEqual(set(info['training_ids']) | set(info['validation_ids']), set(self.fitting))
        self.assertFalse(set(info['training_ids']) & set(info['validation_ids']))
        self.assertFalse((set(info['training_ids']) | set(info['validation_ids'])) & set(self.reserved))
        output = predict_members(models, self.vectors, self.reserved)
        self.assertEqual(output.shape, (5, 5))
        self.assertTrue(np.isfinite(output).all())
        training_values = np.array([self.vectors[i] for i in info['training_ids']])
        validation_values = np.array([self.vectors[i] for i in info['validation_ids']])
        validation_scores = np.array([self.scores[i] for i in info['validation_ids']])
        for model, meta in zip(models[3:], info['members']):
            np.testing.assert_allclose(model.x_mean, training_values.mean(axis=0))
            loss = np.mean(((model.predict(validation_values) - validation_scores) / model.y_scale) ** 2)
            self.assertAlmostEqual(loss, meta['best_validation_mse_normalized'], places=5)
            self.assertLessEqual(meta['best_epoch'], meta['epochs'])
            self.assertLessEqual(meta['epochs'], 200)

    def test_cpu_reproducibility_and_ridge_default(self):
        first, _, meta1 = fit_hybrid_group(self.vectors, self.scores, self.fitting, self.reserved, 7, self.seeds, 'cpu')
        second, _, meta2 = fit_hybrid_group(self.vectors, self.scores, self.fitting, self.reserved, 7, self.seeds, 'cpu')
        self.assertEqual(meta1, meta2)
        np.testing.assert_allclose(predict_members(first, self.vectors, self.reserved),
                                   predict_members(second, self.vectors, self.reserved), rtol=0, atol=1e-7)
        self.assertEqual(len(fit_group(self.vectors, self.scores, self.fitting, self.reserved, 7, self.seeds)[0]), 5)

    def test_rejects_overlap_invalid_device_and_study_scope(self):
        with self.assertRaises(ValueError):
            fit_hybrid_group(self.vectors, self.scores, self.fitting, self.fitting[:1], 7, self.seeds, 'cpu')
        with self.assertRaises(ValueError):
            fit_hybrid_group(self.vectors, self.scores, self.fitting, self.reserved, 7, self.seeds, 'unknown')
        with self.assertRaises(ValueError):
            run_pilot('unused', reward_spec=DEFAULT_SPEC, dataset='ired', hybrid_device='cpu')
        with self.assertRaises(ValueError):
            run_pilot('unused', reward_spec=DEFAULT_SPEC, hybrid_device='cpu', reactive_calibration=True)


if __name__ == '__main__':
    unittest.main()


class HybridPilotTest(unittest.TestCase):
    def test_complete_episode_records_roles_and_predictions(self):
        import copy
        import csv
        import itertools
        import json
        import tempfile
        from pathlib import Path
        from unittest.mock import patch

        from app.datasets.amylase import load_amylase
        from app.experiments.evaluation import evaluate
        from app.features.representations import sequence_id

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            data, reference = root / 'data.csv', root / 'ref.fasta'
            reference.write_text('>synthetic\nAAA\n')
            sequences = ['A' + a + b for a, b in itertools.islice(
                itertools.product('ACDEFGHIKLMNPQRSTVWY', repeat=2), 120)]
            with data.open('w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['sequence', 'target', 'set', 'validation'])
                writer.writerows((seq, math.sin(i / 7), 'train' if i < 110 else 'test', 'False')
                                 for i, seq in enumerate(sequences))
            vectors = {sequence_id(seq): np.array([i / 120, (i % 17) / 17, (i % 11) / 11], dtype=np.float32)
                       for i, seq in enumerate(sequences)}
            spec = copy.deepcopy(DEFAULT_SPEC)
            spec['budget'] = {'rounds': 2, 'batch_size': 10}
            with patch('app.datasets.amylase.DATA', data), patch('app.datasets.amylase.REFERENCE', reference), \
                 patch('app.experiments.prediction_pilot.load_verified_representations', return_value=vectors):
                result = run_pilot(root / 'run', seed=7, reward_spec=spec, hybrid_device='cpu')
            events = [json.loads(line) for line in (root / 'run/run.jsonl').read_text().splitlines()]
            settings = next(e['settings'] for e in events if e['event'] == 'method')
            self.assertEqual(settings['method'], 'esm_hybrid_reward')
            self.assertEqual(settings['hybrid_configuration']['ridge_members'], 3)
            self.assertEqual(settings['hybrid_configuration']['neural_members'], 2)
            self.assertEqual(settings['hybrid_configuration']['device'], 'cpu')
            for event in events:
                if event['event'] != 'method' or 'hybrid_fit' not in event['settings']:
                    continue
                round_settings = event['settings']
                fit = round_settings['hybrid_fit']
                self.assertEqual(set(fit['training_ids']) | set(fit['validation_ids']),
                                 set(round_settings['fitting_ids']))
                self.assertFalse(set(fit['training_ids']) & set(fit['validation_ids']))
                self.assertFalse(set(settings['reserved_ids']) & set(round_settings['fitting_ids']))
                self.assertEqual([m['seed'] for m in fit['members']], round_settings['member_seeds'][3:])
                self.assertGreaterEqual(round_settings['hybrid_fit_seconds'], 0)
            _, scores, train, data_hash, ref_hash = load_amylase(data, reference, 4)
            checked = evaluate(events, scores, set(train), data_hash, ref_hash)
            self.assertEqual(result['batches'], 2)
            self.assertEqual(checked['curve'][-1]['new_measurements'], 20)
            self.assertEqual(checked['stop_reason'], 'budget_exhausted')
