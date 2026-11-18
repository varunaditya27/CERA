import unittest

from app.experiments.local_search import propose_local


class LocalSearchTests(unittest.TestCase):
    def setUp(self):
        self.known = {'p': 'AAAA', 'q': 'CCAA'}
        self.scores = {'p': 10.0, 'q': 9.8}
        self.known_predictions = {'p': 1.0, 'q': 0.8}

    def test_genetic_recombination_and_one_mutation(self):
        candidates = {'c': 'CAAC', 'd': 'CCCC', 'b': 'AACA'}
        predictions = {'c': 2.0, 'd': 5.0, 'b': 2.0}
        result = propose_local('genetic', self.known, self.scores, self.known_predictions,
                               candidates, predictions, 10)
        self.assertEqual(result['parents'], ['p', 'q'])
        self.assertIn('c', result['proposals'])
        self.assertIn('b', result['proposals'])
        self.assertNotIn('d', result['proposals'])
        self.assertEqual(result['selected'], ['b', 'c'])

    def test_rollout_requires_intermediate_prediction(self):
        candidates = {'step': 'AAAC', 'second': 'AACC'}
        low = {'step': 0.5, 'second': 2.0}
        result = propose_local('adalead', self.known, self.scores, self.known_predictions, candidates, low, 10)
        self.assertEqual(result['proposals'], ['step'])
        high = {'step': 1.1, 'second': 2.0}
        result = propose_local('adalead', self.known, self.scores, self.known_predictions, candidates, high, 10)
        self.assertEqual(result['selected'], ['second', 'step'])

    def test_empty_neighborhood_and_overlap(self):
        result = propose_local('genetic', self.known, self.scores, self.known_predictions,
                               {'far': 'GGGG'}, {'far': 1.0}, 10)
        self.assertEqual(result['selected'], [])
        with self.assertRaises(ValueError):
            propose_local('genetic', self.known, self.scores, self.known_predictions,
                          {'p': 'AGGG'}, {'p': 1.0}, 10)

    def test_negative_best_uses_absolute_threshold(self):
        result = propose_local('adalead', self.known, {'p': -1.0, 'q': -1.1}, self.known_predictions,
                               {'x': 'AAAC'}, {'x': 1.0}, 10)
        self.assertEqual(result['parents'], ['p'])
