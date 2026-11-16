"""Random and sequence-based selection for development comparisons."""
import random

from sklearn.linear_model import RidgeCV
from sklearn.model_selection import KFold
from sklearn.preprocessing import OneHotEncoder

ALPHABET = list('ACDEFGHIKLMNPQRSTVWY')
PENALTIES = (0.1, 1.0, 10.0, 100.0)


def choose_random(candidates, count, generator):
    return generator.sample(sorted(candidates), count)


def choose_greedy(sequences, scores, candidates, count, seed):
    known_ids = sorted(scores)
    candidate_ids = sorted(candidates)
    length = len(next(iter(sequences.values())))
    encoder = OneHotEncoder(categories=[ALPHABET] * length, sparse_output=True)
    known = [list(sequences[identifier]) for identifier in known_ids]
    features = encoder.fit_transform(known)
    model = RidgeCV(alphas=PENALTIES, cv=KFold(n_splits=5, shuffle=True, random_state=seed),
                    scoring='neg_mean_squared_error')
    model.fit(features, [scores[identifier] for identifier in known_ids])
    predictions = model.predict(encoder.transform([list(candidates[identifier]) for identifier in candidate_ids]))
    values = {identifier: float(value) for identifier, value in zip(candidate_ids, predictions)}
    selected = sorted(candidate_ids, key=lambda identifier: (-values[identifier], identifier))[:count]
    return selected, values, float(model.alpha_)
