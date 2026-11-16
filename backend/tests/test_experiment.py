import csv
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from app.amylase import DATA, REFERENCE
from app.experiment import Experiment


class ExperimentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.reference = self.root / 'reference.fasta'
        self.reference.write_text('>reference\nAAAAA\n')
        self.data = self.root / 'data.csv'
        with self.data.open('w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['sequence', 'target', 'set', 'validation'])
            writer.writerows([('AAAAA', 1, 'test', 'False'), ('CAAAA', 2, 'train', 'False'),
                              ('ACAAA', 3, 'train', 'True'), ('AACAA', 4, 'test', 'False'),
                              ('CCCCC', 99, 'test', 'False')])

    def make_run(self, name='run.jsonl', **kwargs):
        run = Experiment(self.data, self.reference, self.root / name, seed=42,
                         initial_count=1, budget=kwargs.get('budget', 2), batch_size=2)
        self.addCleanup(run.close)
        return run

    def test_hidden_scores_reproducibility_and_reference(self):
        run = self.make_run()
        other = self.make_run('other.jsonl')
        self.assertEqual(run.revealed, other.revealed)
        self.assertEqual(run.candidates, other.candidates)
        reference_id = hashlib.sha256(b'AAAAA').hexdigest()
        excluded_id = hashlib.sha256(b'CCCCC').hexdigest()
        self.assertIn(reference_id, run.candidates)
        self.assertNotIn(excluded_id, run.candidates)
        log = (self.root / 'run.jsonl').read_text()
        for identifier in run.candidates:
            self.assertNotIn(identifier, log)
        self.assertNotIn(reference_id, json.loads(log)['initial'])
        self.assertEqual(run.reveal([reference_id]), {reference_id: 1.0})

    def test_invalid_batches_are_atomic(self):
        run = self.make_run()
        candidate = next(iter(run.candidates))
        initial_id = next(iter(run.revealed))
        before = (self.root / 'run.jsonl').read_text()
        for ids in ([], [candidate, candidate], [candidate, 'unknown'], [candidate, initial_id],
                    [candidate, candidate, candidate], [hashlib.sha256(b'CCCCC').hexdigest()]):
            with self.subTest(ids=ids), self.assertRaises(ValueError):
                run.reveal(ids)
            self.assertEqual(run.remaining, 2)
            self.assertEqual((self.root / 'run.jsonl').read_text(), before)

    def test_partial_batch_budget_and_log_reconstruction(self):
        run = self.make_run()
        first, second, third = list(run.candidates)
        run.reveal([first])
        with self.assertRaises(ValueError):
            run.reveal([second, third])
        run.reveal([second])
        self.assertEqual(run.stop_reason, 'budget_exhausted')
        with self.assertRaises(ValueError):
            run.reveal([third])
        events = [json.loads(line) for line in (self.root / 'run.jsonl').read_text().splitlines()]
        self.assertEqual([event['event'] for event in events], ['start', 'selection', 'reveal', 'selection', 'reveal'])
        reconstructed = events[0]['initial'].copy()
        for selection, reveal in zip(events[1::2], events[2::2]):
            self.assertEqual(selection['ids'], list(reveal['measurements']))
            reconstructed.update(reveal['measurements'])
        self.assertEqual(reconstructed, run.revealed)
        self.assertEqual(events[-1]['remaining'], 0)

    def test_no_candidates_stop_and_log_not_overwritten(self):
        run = self.make_run(budget=10)
        ids = list(run.candidates)
        run.reveal(ids[:2])
        run.reveal(ids[2:])
        self.assertEqual(run.stop_reason, 'no_candidates')
        with self.assertRaises(FileExistsError):
            self.make_run()

    def test_early_stop_preserves_budget_and_rejects_reveals(self):
        run = self.make_run()
        candidate = next(iter(run.candidates))
        run.stop_early('failed_repairs')
        self.assertEqual(run.remaining, 2)
        self.assertEqual(run.stop_reason, 'failed_repairs')
        with self.assertRaises(ValueError):
            run.reveal([candidate])
        self.assertEqual(json.loads((self.root / 'run.jsonl').read_text().splitlines()[-1]),
                         {'event': 'stop', 'stop_reason': 'failed_repairs', 'remaining': 2})

    def test_local_amylase_feasibility(self):
        run = Experiment(DATA, REFERENCE, self.root / 'real.jsonl', seed=1)
        self.addCleanup(run.close)
        self.assertEqual(len(run.revealed), 100)
        self.assertEqual(len(run.candidates), 3175)
        self.assertEqual(run.remaining, 100)


if __name__ == '__main__':
    unittest.main()
