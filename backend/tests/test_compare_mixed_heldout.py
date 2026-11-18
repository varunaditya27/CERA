import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
from compare_mixed_heldout import compare


class CompareMixedHeldoutTests(unittest.TestCase):
    def test_pairs_and_rejects_changed_assignments(self):
        runs = [{'seed': i, 'initial_ids': ['a'], 'reserved_ids': ['a'], 'member_seeds': [1],
                 'predictions': [['b', 1.]]} for i in range(10)]
        evaluated = [{'seed': i, 'n': 1, 'spearman': None, 'mean_absolute_error': .5, 'covered': 1}
                     for i in range(10)]
        predictions = {'groups': [{'dataset': str(i), 'runs': copy.deepcopy(runs)} for i in range(4)]}
        evaluations = {'groups': [{'dataset': str(i), 'runs': copy.deepcopy(evaluated)} for i in range(4)]}
        ridge = copy.deepcopy(predictions)
        self.assertEqual(compare(predictions, ridge, evaluations, evaluations)[0]['median_paired_difference']['mae'], 0)
        ridge['groups'][0]['runs'][0]['initial_ids'] = ['different']
        with self.assertRaisesRegex(ValueError, 'Matched examples'):
            compare(predictions, ridge, evaluations, evaluations)


if __name__ == '__main__':
    unittest.main()
