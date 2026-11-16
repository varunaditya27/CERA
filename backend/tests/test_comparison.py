import csv
import json
import random
import tempfile
import unittest
from pathlib import Path

from app.comparison import summarize
from app.experiment import Experiment
from app.selection import choose_greedy, choose_random


class ComparisonTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.root = root
        (root / 'reference.fasta').write_text('>reference\nAAAA\n')
        with (root / 'data.csv').open('w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['sequence', 'target', 'set', 'validation'])
            writer.writerows([('AAAA', 0, 'train', 'False'), ('CAAA', 1, 'train', 'False'),
                              ('ACAA', 2, 'train', 'False'), ('AACA', 3, 'train', 'False'),
                              ('AAAC', 4, 'train', 'False'), ('CCAA', 5, 'train', 'False'),
                              ('CACA', 6, 'train', 'False'), ('CAAC', 7, 'train', 'False'),
                              ('ACCA', 8, 'test', 'False'), ('ACAC', 9, 'test', 'False')])

    def make_run(self, name):
        run = Experiment(self.root / 'data.csv', self.root / 'reference.fasta',
                         self.root / name, seed=1, initial_count=6, budget=2, batch_size=2)
        self.addCleanup(run.close)
        return run

    def test_matched_start_and_predictions_recorded_before_reveal(self):
        first, second = self.make_run('one.jsonl'), self.make_run('two.jsonl')
        self.assertEqual(first.revealed, second.revealed)
        self.assertEqual(first.candidates, second.candidates)
        self.assertEqual(set(first.revealed_sequences), set(first.revealed))
        ids, predictions, _ = choose_greedy(first.revealed_sequences, first.revealed,
                                             first.candidates, 2, 1)
        self.assertEqual(len(predictions), len(first.candidates))
        with self.assertRaises(ValueError):
            first.reveal(ids, {ids[0]: float('nan')})
        first.reveal(ids, predictions)
        events = [json.loads(line) for line in (self.root / 'one.jsonl').read_text().splitlines()]
        self.assertEqual([item['event'] for item in events], ['start', 'selection', 'reveal'])
        self.assertEqual(events[1]['predictions'], predictions)
        self.assertEqual(ids, events[1]['ids'])
        rows = summarize(self.root / 'one.jsonl', self.root / 'summary.csv')
        self.assertEqual(rows, [(0, max(events[0]['initial'].values())),
                                (2, max(first.revealed.values()))])

    def test_selection_is_repeatable(self):
        run = self.make_run('repeat.jsonl')
        self.assertEqual(choose_random(run.candidates, 2, random.Random(3)),
                         choose_random(run.candidates, 2, random.Random(3)))
        args = (run.revealed_sequences, run.revealed, run.candidates, 2, 5)
        self.assertEqual(choose_greedy(*args), choose_greedy(*args))


if __name__ == '__main__':
    unittest.main()
