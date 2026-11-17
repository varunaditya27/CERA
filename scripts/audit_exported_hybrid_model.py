#!/usr/bin/env python3
"""Independently refit and verify a saved mixed predictor against its parent episode."""
import argparse
import hashlib
import json
import math
import random
from pathlib import Path

import numpy as np

from app.experiments.hybrid_predictor import fit_hybrid_group, hybrid_configuration
from app.experiments.hybrid_snapshot import load_hybrid_snapshot
from app.experiments.prediction_intervals import interval_radius
from app.experiments.predictor_group import predict_group
from app.features.amylase_representations import CACHE_SHA256, load_verified_representations
from app.provenance.sources import source_hashes
from audit_hybrid_pilot import audit_record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('model', type=Path)
    parser.add_argument('record', type=Path)
    parser.add_argument('specification', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--expected-sha256', required=True)
    parser.add_argument('--seed', type=int, required=True)
    parser.add_argument('--device', choices=('cpu', 'cuda'), required=True)
    parser.add_argument('--repair', action='store_true')
    args = parser.parse_args()
    snapshot = load_hybrid_snapshot(args.model, expected_sha256=args.expected_sha256)
    context = snapshot.metadata['context']
    report = audit_record(args.record, args.specification, args.seed, args.device, args.repair)
    raw = args.record.read_bytes()
    if hashlib.sha256(raw).hexdigest() != report['record_sha256'] or context['record_sha256'] != report['record_sha256']:
        raise ValueError('Parent record mismatch')
    events = [json.loads(line) for line in raw.splitlines()]
    start = events[0]
    setup = next(e['settings'] for e in events if e['event'] == 'method')
    known = dict(start['initial'])
    for event in events:
        if event['event'] == 'reveal':
            known.update(event['measurements'])
    fitting = sorted(set(known) - set(setup['reserved_ids']))
    generator = random.Random(setup['member_seed'])
    for event in events:
        if event['event'] == 'method' and 'member_seeds' in event['settings']:
            if generator.sample(range(2**32), 5) != event['settings']['member_seeds']:
                raise ValueError('Member seed sequence mismatch')
    seeds = generator.sample(range(2**32), 5)
    expected_sources = source_hashes(('hybrid_predictor.py', 'predictor_group.py',
                                      'hybrid_snapshot.py', 'prediction_intervals.py'))
    export_script = Path(__file__).with_name('export_hybrid_model.py')
    if (context['data_sha256'] != start['data_sha256'] or context['reference_sha256'] != start['reference_sha256']
            or context['cache_sha256'] != CACHE_SHA256 or context['fitting_ids'] != fitting
            or context['reserved_ids'] != setup['reserved_ids'] or context['member_seeds'] != seeds
            or context['cv_seed'] != setup['cv_seed'] or context['configuration'] != hybrid_configuration(args.device)
            or context['model_sources'] != expected_sources
            or context['export_script_sha256'] != hashlib.sha256(export_script.read_bytes()).hexdigest()):
        raise ValueError('Saved model provenance or role mismatch')
    vectors = load_verified_representations()
    models, penalty, fit = fit_hybrid_group(vectors, known, fitting, setup['reserved_ids'],
                                             setup['cv_seed'], seeds, args.device)
    saved_fit = context['neural_fit']
    if (penalty != context['ridge_penalty'] or fit['training_ids'] != saved_fit['training_ids']
            or fit['validation_ids'] != saved_fit['validation_ids']
            or len(fit['members']) != len(saved_fit['members'])
            or any(a['seed'] != b['seed'] or a['epochs'] != b['epochs'] or a['best_epoch'] != b['best_epoch']
                   or not math.isclose(a['best_validation_mse_normalized'], b['best_validation_mse_normalized'],
                                       rel_tol=1e-5, abs_tol=1e-6)
                   for a, b in zip(fit['members'], saved_fit['members']))):
        raise ValueError('Refitted model settings mismatch')
    calibration, _ = predict_group(models, vectors, setup['reserved_ids'])
    radius = interval_radius(calibration, [known[i] for i in setup['reserved_ids']])
    if not math.isclose(radius, snapshot.metadata['radius'], rel_tol=1e-5, abs_tol=1e-6):
        raise ValueError('Saved prediction radius mismatch')
    identifiers = sorted(vectors)
    values = np.asarray([vectors[i] for i in identifiers])
    expected_mean, expected_spread = predict_group(models, vectors, identifiers)
    observed = snapshot.predict(values)
    mean_diff = float(np.max(np.abs(observed['mean'] - expected_mean)))
    spread_diff = float(np.max(np.abs(observed['spread'] - expected_spread)))
    if mean_diff > 1e-5 or spread_diff > 1e-5:
        raise ValueError('Saved predictions do not match independent refit')
    result = {'model_sha256': args.expected_sha256, 'record_sha256': report['record_sha256'],
              'known_measurements': len(known), 'fitting_count': len(fitting),
              'range_setting_count': len(setup['reserved_ids']), 'checked_representations': len(identifiers),
              'device_refit': args.device, 'snapshot_inference': 'numpy_cpu',
              'maximum_mean_difference': mean_diff, 'maximum_spread_difference': spread_diff,
              'radius': radius}
    with args.output.open('x', encoding='utf-8') as file:
        json.dump(result, file, indent=2, allow_nan=False)
        file.write('\n')
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
