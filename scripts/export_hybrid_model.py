#!/usr/bin/env python3
"""Audit a completed mixed-predictor episode and export a final numeric model."""
import argparse
import hashlib
import json
import os
import random
import tempfile
from pathlib import Path

import numpy as np

from app.experiments.hybrid_predictor import fit_hybrid_group, hybrid_configuration
from app.experiments.hybrid_snapshot import load_hybrid_snapshot, save_hybrid_snapshot
from app.experiments.prediction_intervals import interval_radius
from app.experiments.predictor_group import predict_group
from app.features.amylase_representations import CACHE_SHA256, load_verified_representations
from app.provenance.sources import source_hashes
from audit_hybrid_pilot import audit_record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('record', type=Path)
    parser.add_argument('specification', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--seed', type=int, required=True)
    parser.add_argument('--device', choices=('cpu', 'cuda'), required=True)
    parser.add_argument('--repair', action='store_true')
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('Output already exists')
    audit = audit_record(args.record, args.specification, args.seed, args.device, args.repair)
    raw = args.record.read_bytes()
    if hashlib.sha256(raw).hexdigest() != audit['record_sha256']:
        raise ValueError('Run record changed after audit')
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
                raise ValueError('Recorded member seed sequence mismatch')
    seeds = generator.sample(range(2**32), 5)
    vectors = load_verified_representations()
    models, penalty, fit = fit_hybrid_group(vectors, known, fitting, setup['reserved_ids'],
                                             setup['cv_seed'], seeds, args.device)
    calibration, _ = predict_group(models, vectors, setup['reserved_ids'])
    radius = interval_radius(calibration, [known[i] for i in setup['reserved_ids']])
    context = {'record_sha256': audit['record_sha256'], 'data_sha256': start['data_sha256'],
               'reference_sha256': start['reference_sha256'], 'cache_sha256': CACHE_SHA256,
               'fitting_ids': fitting, 'reserved_ids': setup['reserved_ids'], 'member_seeds': seeds,
               'cv_seed': setup['cv_seed'], 'ridge_penalty': penalty, 'neural_fit': fit,
               'configuration': hybrid_configuration(args.device),
               'model_sources': source_hashes(('hybrid_predictor.py', 'predictor_group.py',
                                                'hybrid_snapshot.py', 'prediction_intervals.py')),
               'export_script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=args.output.parent, prefix='.hybrid-export-') as directory:
        candidate = Path(directory) / 'model.npz'
        save_hybrid_snapshot(candidate, models, radius, context)
        loaded = load_hybrid_snapshot(candidate)
        identifiers = sorted(vectors)
        inputs = np.asarray([vectors[i] for i in identifiers])
        expected_mean, expected_spread = predict_group(models, vectors, identifiers)
        actual = loaded.predict(inputs)
        mean_diff = float(np.max(np.abs(actual['mean'] - expected_mean)))
        spread_diff = float(np.max(np.abs(actual['spread'] - expected_spread)))
        if mean_diff > 1e-5 or spread_diff > 1e-5:
            raise ValueError('Exported model predictions differ from fitted models')
        os.link(candidate, args.output)
    print(json.dumps({'output': str(args.output), 'model_sha256': hashlib.sha256(args.output.read_bytes()).hexdigest(),
                      'known_measurements': len(known), 'fitting_count': len(fitting),
                      'range_setting_count': len(setup['reserved_ids']), 'refit_candidates_checked': len(identifiers),
                      'maximum_mean_difference': mean_diff, 'maximum_spread_difference': spread_diff,
                      'radius': radius}, sort_keys=True))


if __name__ == '__main__':
    main()
