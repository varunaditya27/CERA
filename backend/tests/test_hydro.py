import tempfile
import unittest
import copy
import csv
import itertools
import json
from pathlib import Path
from unittest.mock import patch

import numpy as np

from app.datasets.hydro import DATA, PROTEINS, REFERENCES, load_hydro
from app.experiments.experiment import Experiment
from app.experiments.prediction_pilot import run_pilot
from app.features.hydro_representations import load_verified_representations
from app.features.representations import sequence_id
from app.llm.goal_compiler import DEFAULT_SPEC


class HydroTests(unittest.TestCase):
    def test_separate_protein_counts_and_score_free_caches(self):
        counts = {'P06241': (1010, 263, 9972), 'P01053': (1292, 713, 6463),
                  'P0A9X9': (2916, 701, 8500)}
        for protein, (eligible, initial_pool, cache_size) in counts.items():
            with self.subTest(protein=protein):
                sequences, scores, train, _, _ = load_hydro(DATA, REFERENCES[protein], 4)
                self.assertEqual((len(sequences), len(train)), (eligible, initial_pool))
                self.assertTrue(all(len(sequence) == PROTEINS[protein] for sequence in sequences.values()))
                vectors = load_verified_representations(protein)
                self.assertEqual(len(vectors), cache_size)
                self.assertTrue(set(sequences).issubset(vectors))
                self.assertEqual(next(iter(vectors.values())).shape, (320,))
                with tempfile.TemporaryDirectory() as temp:
                    run = Experiment(DATA, REFERENCES[protein], Path(temp) / 'run.jsonl',
                                     seed=2, loader=load_hydro)
                    try:
                        self.assertEqual(len(run.revealed), 100)
                        self.assertEqual(len(run.candidates), eligible - 100)
                        identifier = next(iter(run.candidates))
                        self.assertEqual(run.reveal([identifier]), {identifier: scores[identifier]})
                    finally:
                        run.close()

    def test_wrong_reference_and_unknown_protein_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            wrong = Path(temp) / 'wrong.fasta'
            wrong.write_text('>wrong\n' + 'A' * 57 + '\n')
            with self.assertRaises(ValueError):
                load_verified_representations('P06241', reference_path=wrong)
        with self.assertRaises(ValueError):
            load_verified_representations('unknown')

    def test_hydro_dispatch_with_synthetic_data(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            data, reference = root / 'data.csv', root / 'reference.fasta'
            reference.write_text('>synthetic\n' + 'A' * 57 + '\n')
            alphabet = 'ACDEFGHIKLMNPQRSTVWY'
            sequences = ['A' * 55 + a + b for a, b in itertools.islice(itertools.product(alphabet, repeat=2), 120)]
            with data.open('w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['sequence', 'target', 'set', 'validation'])
                writer.writerows((sequence, index / 100, 'train' if index < 110 else 'test', 'False')
                                 for index, sequence in enumerate(sequences))
            vectors = {sequence_id(sequence): np.asarray([index / 120, (index % 19) / 19], dtype=np.float32)
                       for index, sequence in enumerate(sequences)}
            spec = copy.deepcopy(DEFAULT_SPEC)
            spec['budget'] = {'rounds': 1, 'batch_size': 1}
            with patch('app.datasets.hydro.DATA', data), patch.dict('app.datasets.hydro.REFERENCES', {'P06241': reference}), \
                 patch('app.features.hydro_representations.load_verified_representations', return_value=vectors):
                result = run_pilot(root / 'run', seed=7, reward_spec=spec, dataset='hydro-P06241')
            events = [json.loads(line) for line in (root / 'run/run.jsonl').read_text().splitlines()]
            self.assertEqual(result['batches'], 1)
            self.assertEqual(next(e['settings']['dataset'] for e in events if e['event'] == 'method'), 'hydro-P06241')
            self.assertEqual(next(e['remaining'] for e in events if e['event'] == 'reveal'), 0)
