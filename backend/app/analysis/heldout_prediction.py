"""Predict held-out benchmark variants using selected training measurements only."""
import random

from app.experiments.predictor_group import fit_group, predict_group
from app.experiments.prediction_intervals import interval_radius


def predict_heldout(vectors, training_scores, test_ids, seed):
    initial = sorted(training_scores)
    test_ids = sorted(test_ids)
    if (len(initial) != 100 or len(test_ids) != len(set(test_ids)) or not test_ids
            or set(initial) & set(test_ids)):
        raise ValueError('Invalid selected training scores or held-out identifiers')
    reserved = sorted(random.Random(2000 + seed).sample(initial, 20))
    fitting = sorted(set(initial) - set(reserved))
    member_seeds = random.Random(3000 + seed).sample(range(2**32), 5)
    models, penalty = fit_group(vectors, training_scores, fitting, reserved, seed, member_seeds)
    calibration, _ = predict_group(models, vectors, reserved)
    radius = interval_radius(calibration, [training_scores[i] for i in reserved])
    means, _ = predict_group(models, vectors, test_ids)
    return {'seed': seed, 'initial_ids': initial, 'reserved_ids': reserved, 'member_seeds': member_seeds,
            'penalty': penalty, 'radius': radius,
            'predictions': [[identifier, float(value)] for identifier, value in zip(test_ids, means)]}
