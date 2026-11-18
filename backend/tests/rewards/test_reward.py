import copy
import random
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

    def test_vectorized_results_match_direct_calculation(self):
        rng = random.Random(1729)
        alphabet = 'ACDEFGHIKLMNPQRSTVWY'
        sequences = ['A' * 18 + a + b for a in alphabet[:7] for b in alphabet[:7]]
        candidates = {f'{index:02d}': {'sequence': sequence, 'mean': rng.random(),
                                      'spread': rng.random(), 'distance': rng.random()}
                      for index, sequence in enumerate(sequences)}
        spec = specification()
        spec['hard_constraints']['max_mutations'] = 2
        expected = []
        for _ in range(3):
            values = []
            for identifier, row in candidates.items():
                if identifier in [item['id'] for item in expected]:
                    continue
                diversity = min((sum(a != b for a, b in zip(row['sequence'], candidates[item['id']]['sequence'])) / 20
                                 for item in expected), default=0.0)
                reward = row['mean'] - 0.5 * row['spread'] - 0.3 * row['distance'] + diversity
                values.append((reward, identifier, diversity))
            reward, identifier, diversity = min(values, key=lambda item: (-item[0], item[1]))
            expected.append({'id': identifier, 'reward': reward, 'diversity': diversity})
        self.assertEqual(select_batch(spec, candidates, 'A' * 20, 3), expected)
