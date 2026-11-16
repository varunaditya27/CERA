"""Finite-pool recombination and AdaLead-style neighborhood search."""
import itertools
import math

import numpy as np
from scipy.spatial.distance import cdist


def _matrix(sequences):
    return np.asarray([list(sequence.encode('ascii')) for sequence in sequences], dtype=np.uint8)


def _distances(left, right, length):
    return np.rint(cdist(left, right, metric='hamming') * length).astype(int)


def propose_local(method, known_sequences, known_scores, known_predictions, candidates, predictions, count):
    if (method not in ('genetic', 'adalead') or set(known_sequences) != set(known_scores)
            or set(known_sequences) != set(known_predictions) or set(candidates) != set(predictions)
            or set(known_sequences) & set(candidates) or not known_sequences
            or not isinstance(count, int) or isinstance(count, bool) or count < 1):
        raise ValueError('Invalid local search inputs')
    if any(not math.isfinite(x) for x in (*known_scores.values(), *known_predictions.values(), *predictions.values())):
        raise ValueError('Invalid local search scores')
    known_ids, candidate_ids = sorted(known_sequences), sorted(candidates)
    sequences = [known_sequences[i] for i in known_ids] + [candidates[i] for i in candidate_ids]
    if (not sequences or any(not isinstance(s, str) or not s or len(s) != len(sequences[0]) for s in sequences)
            or len(sequences) != len(set(sequences))):
        raise ValueError('Invalid local search sequences')
    parents = sorted(known_ids, key=lambda i: (-known_scores[i], i))[:10]
    if method == 'adalead':
        best = known_scores[parents[0]]
        parents = [i for i in parents if known_scores[i] >= best - 0.05 * abs(best)]
    if not candidate_ids:
        return {'parents': parents, 'proposals': [], 'selected': []}
    length = len(sequences[0])
    all_matrix = _matrix(sequences)
    candidate_matrix = all_matrix[len(known_ids):]
    parent_matrix = _matrix([known_sequences[i] for i in parents])
    parent_distance = _distances(all_matrix, parent_matrix, length)
    candidate_parent = parent_distance[len(known_ids):]
    reachable = np.any(candidate_parent <= 2, axis=1)
    if method == 'genetic':
        parent_sequences = [known_sequences[i] for i in parents]
        recombinants = set(parent_sequences)
        for left, right in itertools.permutations(parent_sequences, 2):
            for index, (a, b) in enumerate(zip(left, right)):
                if a != b and index + 1 < length:
                    recombinants.add(left[:index + 1] + right[index + 1:])
        nearby = _distances(candidate_matrix, _matrix(sorted(recombinants)), length)
        proposed = reachable & np.any(nearby <= 1, axis=1)
    else:
        all_predictions = [known_predictions[i] for i in known_ids] + [predictions[i] for i in candidate_ids]
        proposed = np.zeros(len(candidate_ids), dtype=bool)
        for column, parent in enumerate(parents):
            proposed |= candidate_parent[:, column] == 1
            intermediate = [index for index, distance in enumerate(parent_distance[:, column])
                            if distance == 1 and all_predictions[index] >= known_predictions[parent]]
            if intermediate:
                neighbors = _distances(candidate_matrix, all_matrix[intermediate], length)
                proposed |= (candidate_parent[:, column] <= 2) & np.any(neighbors == 1, axis=1)
    proposal_ids = [identifier for identifier, include in zip(candidate_ids, proposed) if include]
    ranked = sorted(proposal_ids, key=lambda i: (-predictions[i], i))
    return {'parents': parents, 'proposals': proposal_ids, 'selected': ranked[:count]}
