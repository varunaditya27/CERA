import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
from audit_mixed_round_refits import audit_rounds


class MixedRoundRefitTests(unittest.TestCase):
    def events(self):
        setup = {'reserved_ids': ['reserved'], 'cv_seed': 1}
        fit = {'fitting_ids': ['fit'], 'member_seeds': [1], 'penalty': 1,
               'hybrid_fit': {'training_ids': ['fit'], 'validation_ids': []}}
        selection = {'event': 'selection', 'prediction_ranges': {'candidate': {'mean': 1., 'spread': .2}}}
        return ([{'event': 'start', 'initial': {'reserved': 0., 'fit': 1.}},
                 {'event': 'method', 'settings': setup}]
                + sum(([{'event': 'method', 'settings': fit}, selection] for _ in range(10)), []))

    @patch('audit_mixed_round_refits.predict_group', return_value=([1.], [.2]))
    @patch('audit_mixed_round_refits.fit_hybrid_group', return_value=([], 1, {'training_ids': ['fit'], 'validation_ids': []}))
    def test_checks_all_rounds_and_rejects_changed_prediction(self, fit, predict):
        events = self.events()
        self.assertEqual(audit_rounds(events, {}, 'cpu')['rounds'], 10)
        events[-1] = {'event': 'selection', 'prediction_ranges': {'candidate': {'mean': 2., 'spread': .2}}}
        with self.assertRaisesRegex(ValueError, 'Refit mean differs'):
            audit_rounds(events, {}, 'cpu')
        events[-1]['prediction_ranges']['candidate']['mean'] = float('nan')
        with self.assertRaisesRegex(ValueError, 'Invalid refit predictions'):
            audit_rounds(events, {}, 'cpu')

    def test_rejects_unrevealed_fitting_example(self):
        events = self.events()
        events[2]['settings'] = dict(events[2]['settings'], fitting_ids=['unrevealed'])
        with self.assertRaisesRegex(ValueError, 'revealed measurements'):
            audit_rounds(events, {}, 'cpu')


if __name__ == '__main__':
    unittest.main()
