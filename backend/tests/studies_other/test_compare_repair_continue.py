import unittest

import json

from scripts.multiprotein.compare_repair_continue import classify
from scripts.multiprotein.recount_repair_continue import best_and_count


class CompareRepairContinueTests(unittest.TestCase):
    def test_ties_use_the_study_tolerance(self):
        self.assertEqual(classify(1.0 + 1e-13, 1.0), 'tied')
        self.assertEqual(classify(1.1, 1.0), 'higher')
        self.assertEqual(classify(0.9, 1.0), 'lower')

    def test_recount_takes_the_best_revealed_score(self):
        lines = [json.dumps({'event': 'start', 'initial': {'a': 1.0, 'b': 2.0}}),
                 json.dumps({'event': 'reveal', 'measurements': {'c': 5.0, 'd': 3.0}}),
                 json.dumps({'event': 'reveal', 'measurements': {'e': 4.0}})]
        self.assertEqual(best_and_count(lines), (5.0, 3))


if __name__ == '__main__':
    unittest.main()
