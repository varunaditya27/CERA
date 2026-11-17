import importlib.util
from pathlib import Path
import unittest


spec = importlib.util.spec_from_file_location(
    'evaluate_exported_hybrid', Path(__file__).resolve().parents[2] / 'scripts/evaluate_exported_hybrid.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class EvaluationMetricsTest(unittest.TestCase):
    def test_metrics_and_invalid_input(self):
        result = module.metrics([1, 3], [2, 3], 0.5)
        self.assertEqual(result['count'], 2)
        self.assertEqual(result['mean_absolute_error'], 0.5)
        self.assertEqual(result['covered'], 1)
        self.assertEqual(result['coverage'], 0.5)
        for predictions, scores, radius in [([], [], 1), ([1], [1, 2], 1), ([float('nan')], [1], 1), ([1], [1], -1)]:
            with self.assertRaises(ValueError):
                module.metrics(predictions, scores, radius)
