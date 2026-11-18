import copy
import sys
import unittest
from pathlib import Path
from scripts.reporting import analyze_paired_study as analysis
from scipy.stats import PermutationMethod, wilcoxon


class PairedStudyAnalysisTest(unittest.TestCase):
    def test_signed_rank_ties_and_all_zero(self):
        self.assertIsNone(analysis.signed_rank([0, 0]))
        self.assertEqual(analysis.signed_rank([1, 1, 0]), 0.5)
        self.assertEqual(analysis.signed_rank([1, -1]), 1)
        self.assertIsNone(analysis.signed_rank([1e-13]))

    def test_matches_scipy_permutation_with_ties(self):
        values = [1, -2, 2, 3]
        expected = wilcoxon(values, method=PermutationMethod(n_resamples=2 ** len(values))).pvalue
        self.assertEqual(analysis.signed_rank(values), expected)

    def test_pairing_and_missing_records(self):
        groups = []
        for dataset in analysis.GROUPS:
            rows = [{'seed': seed, 'method': method, 'status': 'completed',
                     'best_observed': 1 if method == 'fixed' else 2, 'new_measurements': 10}
                    for seed in analysis.SEEDS for method in ('fixed', *analysis.METHODS)]
            groups.append({'dataset': dataset, 'summaries': rows})
        report = {'groups': groups}
        result = analysis.analyze(report)
        self.assertEqual(len(result), 8)
        self.assertEqual(result[0]['mean_difference'], 1)
        self.assertEqual(result[0]['percentile_interval_95'], [1, 1])
        self.assertEqual(result[0]['signed_rank_p'], 2 / 1024)
        broken = copy.deepcopy(report)
        broken['groups'][0]['summaries'].pop()
        with self.assertRaises(ValueError):
            analysis.analyze(broken)


if __name__ == '__main__':
    unittest.main()
