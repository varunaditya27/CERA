import copy
import unittest

from app.rewards.reward_selection import select_batch
from app.rewards.reward_spec import validate_spec


def specification():
    return {'goal': 'maximize_fitness',
            'terms': {'uncertainty_penalty': {'weight': 0.5, 'allowed_range': [0.0, 2.0]},
                      'distance_penalty': {'weight': 0.3, 'allowed_range': [0.0, 2.0]},
                      'diversity_bonus': {'weight': 1.0, 'allowed_range': [0.0, 1.0]}},
            'hard_constraints': {'max_mutations': 1}, 'budget': {'rounds': 10, 'batch_size': 3},
            'abstain_after_failed_repairs': 2}


class RewardTests(unittest.TestCase):
    def test_spec_rejects_extra_fields_and_expanded_ranges(self):
        spec = specification()
        validate_spec(spec)
        for bad in ('extra', 'range', 'weight', 'bool'):
            altered = copy.deepcopy(spec)
            if bad == 'extra':
                altered['terms']['arbitrary_code'] = 'ignored'
            elif bad == 'range':
                altered['terms']['uncertainty_penalty']['allowed_range'] = [0, 100]
            elif bad == 'weight':
                altered['terms']['distance_penalty']['weight'] = float('nan')
            else:
                altered['budget']['batch_size'] = True
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                validate_spec(altered)

    def test_ranking_penalties_diversity_constraints_and_ties(self):
        candidates = {
            'a': {'sequence': 'AAAA', 'mean': 1.0, 'spread': 0.0, 'distance': 0.0},
            'b': {'sequence': 'AAAC', 'mean': 0.9, 'spread': 0.0, 'distance': 0.0},
            'c': {'sequence': 'AACA', 'mean': 0.9, 'spread': 0.0, 'distance': 0.0},
            'd': {'sequence': 'ACAA', 'mean': 2.0, 'spread': 2.0, 'distance': 1.0},
            'invalid': {'sequence': 'ACCA', 'mean': 100.0, 'spread': 0.0, 'distance': 0.0},
        }
        chosen = select_batch(specification(), candidates, 'AAAA', 3)
        self.assertEqual([x['id'] for x in chosen], ['a', 'b', 'c'])
        self.assertAlmostEqual(chosen[1]['diversity'], 0.25)
        self.assertAlmostEqual(chosen[1]['reward'], 1.15)
        self.assertEqual(len(select_batch(specification(), candidates, 'AAAA', 1)), 1)
        self.assertEqual(select_batch(specification(), candidates, 'AAAA', 0), [])

    def test_invalid_features_fail_even_when_candidate_is_ineligible(self):
        candidate = {'x': {'sequence': 'ACCA', 'mean': 1, 'spread': -1, 'distance': 0}}
        with self.assertRaises(ValueError):
            select_batch(specification(), candidate, 'AAAA', 1)

    def test_only_out_of_constraint_candidates(self):
        candidate = {'x': {'sequence': 'ACCA', 'mean': 1, 'spread': 0, 'distance': 0}}
        self.assertEqual(select_batch(specification(), candidate, 'AAAA', 3), [])

    def test_duplicate_sequences_rejected(self):
        candidate = {'sequence': 'AAAC', 'mean': 1, 'spread': 0, 'distance': 0}
        with self.assertRaises(ValueError):
            select_batch(specification(), {'x': candidate, 'y': candidate}, 'AAAA', 2)
