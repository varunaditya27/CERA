import tempfile
import unittest
import copy
import csv
import itertools
import json
from pathlib import Path
from unittest.mock import patch

from app.datasets.amylase import load_amylase
from app.experiments.experiment import Experiment
from app.datasets.ired import DATA, REFERENCE
from app.features.ired_representations import CACHE, load_verified_representations
from app.llm.goal_compiler import DEFAULT_SPEC
from app.experiments.prediction_pilot import run_pilot
from app.features.representations import sequence_id
import numpy as np


class IredTests(unittest.TestCase):
    def test_source_counts_and_measurement_boundary(self):
        sequences, scores, train, _, _ = load_amylase(DATA, REFERENCE, 4)
        self.assertEqual((len(sequences), len(scores), len(train)), (7633, 7633, 4408))
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'run.jsonl'
            run = Experiment(DATA, REFERENCE, path, seed=1)
            try:
                self.assertEqual(len(run.revealed), 100)
                self.assertEqual(len(run.candidates), 7533)
                self.assertEqual(run.remaining, 100)
                chosen = next(iter(run.candidates))
                self.assertNotIn(chosen, path.read_text())
                self.assertEqual(run.reveal([chosen]), {chosen: scores[chosen]})
            finally:
                run.close()

    def test_verified_score_free_representations_and_wrong_reference(self):
        vectors = load_verified_representations()
        self.assertEqual(len(vectors), 8586)
        self.assertEqual(next(iter(vectors.values())).shape, (320,))
        with np.load(CACHE, allow_pickle=False) as archive:
            self.assertEqual(set(archive.files), {'identifiers', 'vectors', 'metadata'})
        with tempfile.TemporaryDirectory() as temp:
            wrong = Path(temp) / 'reference.fasta'
            wrong.write_text('>wrong\nAAAA\n')
            with self.assertRaises(ValueError):
                load_verified_representations(reference_path=wrong)

    def test_dataset_dispatch_runs_on_synthetic_ired_format(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            data, reference = root / 'data.csv', root / 'reference.fasta'
            reference.write_text('>synthetic\nAAA\n')
            sequences = ['A' + a + b for a, b in itertools.islice(itertools.product('ACDEFGHIKLMNPQRSTVWY', repeat=2), 120)]
            with data.open('w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['sequence', 'target', 'set', 'validation'])
                writer.writerows((sequence, index / 100, 'train' if index < 110 else 'test', 'False')
                                 for index, sequence in enumerate(sequences))
            vectors = {sequence_id(sequence): np.asarray([index / 120, (index % 19) / 19], dtype=np.float32)
                       for index, sequence in enumerate(sequences)}
            spec = copy.deepcopy(DEFAULT_SPEC)
            spec['budget'] = {'rounds': 1, 'batch_size': 1}
            with patch('app.datasets.ired.DATA', data), patch('app.datasets.ired.REFERENCE', reference), \
                 patch('app.features.ired_representations.load_verified_representations', return_value=vectors):
                result = run_pilot(root / 'run', seed=7, reward_spec=spec, dataset='ired')
            events = [json.loads(line) for line in (root / 'run/run.jsonl').read_text().splitlines()]
            self.assertEqual(result['batches'], 1)
            self.assertEqual(next(e['settings']['dataset'] for e in events if e['event'] == 'method'), 'ired')
            self.assertEqual(next(e['remaining'] for e in events if e['event'] == 'reveal'), 0)
