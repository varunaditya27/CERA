import copy
import sys
import unittest
from pathlib import Path
from scripts.multiprotein.summarize_hydro_low_fitness import DATASETS, METHODS, summarize


class HydroSummaryTest(unittest.TestCase):
    def test_counts_ties_and_missing_runs(self):
        rows = [{'seed': seed, 'method': method, 'status': 'completed', 'new_measurements': 10,
                 'best_observed': 1 if method == 'fixed' else 2, 'stop_reason': 'budget_exhausted',
                 'selected_split_counts': {'train': 3, 'test': 7}, 'covered': None, 'range_count': 0,
                 'repairs_accepted': 0, 'advice_gemini': 0, 'advice_fallback': 0,
                 'advice_request_attempts': 0, 'advice_reported_tokens': 0}
                for seed in range(141, 151) for method in METHODS]
        report = {'scope': 'hydro_low_fitness', 'groups': [{'dataset': d, 'summaries': copy.deepcopy(rows),
                                                                  'curves': [{'seed': seed, 'method': 'fixed',
                                                                              'new_measurements': 10, 'best_observed': 1}
                                                                             for seed in range(141, 151)]} for d in DATASETS]}
        result = summarize(report)
        self.assertEqual(result[0]['methods'][0]['higher_equal_lower_vs_fixed'], [10, 0, 0])
        self.assertEqual(result[0]['methods'][0]['selected_test'], 70)
        self.assertIsNone(result[0]['methods'][0]['covered'])
        self.assertEqual(result[0]['methods'][0]['higher_equal_lower_same_measurements'], [10, 0, 0])
        self.assertEqual(result[0]['methods'][METHODS.index('fixed')]['higher_equal_lower_vs_fixed'], [0, 10, 0])
        broken = copy.deepcopy(report)
        broken['groups'][0]['summaries'].pop()
        with self.assertRaises(ValueError):
            summarize(broken)
        broken = copy.deepcopy(report)
        broken['groups'][0]['summaries'][0]['selected_split_counts']['test'] = 6
        with self.assertRaises(ValueError):
            summarize(broken)


if __name__ == '__main__':
    unittest.main()
