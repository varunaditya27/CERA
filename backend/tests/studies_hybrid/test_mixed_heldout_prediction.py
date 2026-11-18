import unittest
from unittest.mock import patch

from app.analysis.mixed_heldout_prediction import predict_mixed_heldout


class MixedHeldoutTests(unittest.TestCase):
    @patch('app.analysis.mixed_heldout_prediction.predict_group')
    @patch('app.analysis.mixed_heldout_prediction.fit_hybrid_group')
    def test_training_roles_and_heldout_predictions(self, fit, predict):
        scores = {f'train-{i:03}': float(i) for i in range(100)}
        fit.return_value = ([], 1., {'training_ids': [], 'validation_ids': [], 'members': []})
        predict.side_effect = [([0.] * 20, None), ([3., 4.], None)]
        result = predict_mixed_heldout({}, scores, ['test-b', 'test-a'], 121, 'cpu')
        self.assertEqual(result['predictions'], [['test-a', 3.], ['test-b', 4.]])
        args = fit.call_args.args
        self.assertEqual(len(args[2]), 80)
        self.assertEqual(len(args[3]), 20)
        self.assertFalse(set(args[2]) & set(args[3]))
        self.assertFalse({'test-a', 'test-b'} & set(args[1]))
        with self.assertRaises(ValueError):
            predict_mixed_heldout({}, scores, ['train-001'], 121, 'cpu')


if __name__ == '__main__':
    unittest.main()
