#!/usr/bin/env python3
"""Compare the saved development model and matched ridge group on unseen Amylase scores."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from app.datasets.amylase import DATA, REFERENCE, load_amylase
from app.predictors.hybrid_snapshot import load_hybrid_snapshot
from app.predictors.prediction_intervals import interval_radius
from app.predictors.predictor_group import fit_group, predict_group
from app.features.amylase_representations import CACHE_SHA256, load_verified_representations


def metrics(predictions, scores, radius):
    predictions = np.asarray(predictions, dtype=float)
    scores = np.asarray(scores, dtype=float)
    if (predictions.ndim != 1 or not predictions.size or predictions.shape != scores.shape
            or not np.isfinite(predictions).all() or not np.isfinite(scores).all()
            or not np.isfinite(radius) or radius < 0):
        raise ValueError('Invalid evaluation values')
    errors = np.abs(predictions - scores)
    return {'count': len(scores), 'mean_absolute_error': float(errors.mean()),
            'root_mean_squared_error': float(np.sqrt(np.mean(errors ** 2))),
            'covered': int(np.count_nonzero(errors <= radius)),
            'coverage': float(np.mean(errors <= radius)), 'range_width': float(2 * radius)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('model', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--expected-sha256', required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('Output already exists')
    model = load_hybrid_snapshot(args.model, expected_sha256=args.expected_sha256)
    context = model.metadata['context']
    _, scores, _, data_hash, ref_hash = load_amylase(DATA, REFERENCE, 4)
    if (context['data_sha256'] != data_hash or context['reference_sha256'] != ref_hash
            or context['cache_sha256'] != CACHE_SHA256):
        raise ValueError('Model source fingerprints do not match')
    fitting, reserved = context['fitting_ids'], context['reserved_ids']
    known = set(fitting) | set(reserved)
    if (len(known) != len(fitting) + len(reserved) or not known <= scores.keys()):
        raise ValueError('Invalid recorded model roles')
    unseen = sorted(set(scores) - known)
    if not unseen:
        raise ValueError('No unseen eligible scores')
    vectors = load_verified_representations()
    observed_scores = {i: scores[i] for i in known}
    ridge, penalty = fit_group(vectors, observed_scores, fitting, reserved,
                               context['cv_seed'], context['member_seeds'])
    calibration, _ = predict_group(ridge, vectors, reserved)
    ridge_radius = interval_radius(calibration, [observed_scores[i] for i in reserved])
    ridge_predictions, _ = predict_group(ridge, vectors, unseen)
    mixed_predictions = model.predict([vectors[i] for i in unseen])['mean']
    truth = [scores[i] for i in unseen]
    result = {'model_sha256': args.expected_sha256, 'data_sha256': data_hash,
              'reference_sha256': ref_hash, 'cache_sha256': CACHE_SHA256,
              'evaluation_ids_sha256': hashlib.sha256('\n'.join(unseen).encode()).hexdigest(),
              'fitting_count': len(fitting), 'range_setting_count': len(reserved),
              'ridge_penalty': penalty, 'mixed': metrics(mixed_predictions, truth, model.metadata['radius']),
              'ridge': metrics(ridge_predictions, truth, ridge_radius)}
    with args.output.open('x', encoding='utf-8') as file:
        json.dump(result, file, indent=2, allow_nan=False)
        file.write('\n')
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
