#!/usr/bin/env python3
"""Verify a mixed-predictor development run and refit its first group."""
import argparse
import hashlib
import json
import math
from collections import Counter
from pathlib import Path

import numpy as np

from app.datasets.amylase import DATA, REFERENCE, load_amylase
from app.experiments.evaluation import evaluate
from app.predictors.hybrid_predictor import fit_hybrid_group, hybrid_configuration
from app.predictors.predictor_group import predict_group
from app.features.amylase_representations import CACHE_SHA256, load_verified_representations
from app.provenance.sources import source_hashes
from scripts.repair.audit_development_repairs import audit_run


def audit_record(record, specification, seed, device, repair):
    record, specification = Path(record), Path(specification)
    raw = record.read_bytes()
    events = [json.loads(line) for line in raw.splitlines()]
    setup = next(e['settings'] for e in events if e['event'] == 'method')
    spec_raw = specification.read_bytes()
    if (setup['dataset'] != 'amylase' or setup['method'] != 'esm_hybrid_reward'
            or setup['hybrid_device'] != device or setup['hybrid_configuration'] != hybrid_configuration(device)
            or setup['hybrid_source_sha256'] != source_hashes(('hybrid_predictor.py',))
            or setup['source_sha256'] != source_hashes(tuple(setup['source_sha256']))
            or setup['cache_sha256'] != CACHE_SHA256 or setup['repair'] is not repair
            or setup['reward_spec'] != json.loads(spec_raw)
            or setup['reward_origin'] != {'input_sha256': hashlib.sha256(spec_raw).hexdigest(), 'source': 'specification_file'}
            or setup['role_seed'] != 3 or setup['member_seed'] != 4):
        raise ValueError('Pilot settings or source fingerprint mismatch')
    sequences, scores, train, data_hash, ref_hash = load_amylase(DATA, REFERENCE, 4)
    if events[0]['seed'] != seed:
        raise ValueError('Seed mismatch')
    evaluation = evaluate(events, scores, set(train), data_hash, ref_hash)
    row = {'status': 'completed', **evaluation['curve'][-1], 'stop_reason': evaluation['stop_reason'],
           'covered': evaluation['covered'], 'range_count': evaluation['range_count'],
           'mean_range_width': evaluation['mean_range_width']}
    row['found_top_one_percent'] = str(row['found_top_one_percent'])
    counts = Counter()
    method = 'direct' if repair else 'fixed'
    audit_run(events, seed, method, sequences, scores, train,
              {'data_sha256': data_hash, 'reference_sha256': ref_hash}, row, counts,
              hybrid_device=device, role_seed=3, member_seed=4)
    first = next(e['settings'] for e in events if e['event'] == 'method' and 'hybrid_fit' in e['settings'])
    selection = next(e for e in events if e['event'] == 'selection')
    vectors = load_verified_representations()
    models, penalty, metadata = fit_hybrid_group(vectors, events[0]['initial'], first['fitting_ids'],
                                                  setup['reserved_ids'], setup['cv_seed'], first['member_seeds'], device)
    if (penalty != first['penalty'] or metadata['training_ids'] != first['hybrid_fit']['training_ids']
            or metadata['validation_ids'] != first['hybrid_fit']['validation_ids']
            or any(a['seed'] != b['seed'] or a['epochs'] != b['epochs'] or a['best_epoch'] != b['best_epoch']
                   or not math.isclose(a['best_validation_mse_normalized'], b['best_validation_mse_normalized'],
                                       rel_tol=1e-5, abs_tol=1e-6)
                   for a, b in zip(metadata['members'], first['hybrid_fit']['members']))):
        raise ValueError('First-round refit metadata mismatch')
    identifiers = sorted(selection['prediction_ranges'])
    means, spreads = predict_group(models, vectors, identifiers)
    mean_diff = max(abs(float(means[n]) - selection['prediction_ranges'][i]['mean']) for n, i in enumerate(identifiers))
    spread_diff = max(abs(float(spreads[n]) - selection['prediction_ranges'][i]['spread']) for n, i in enumerate(identifiers))
    if mean_diff > 1e-5 or spread_diff > 1e-5:
        raise ValueError('First-round refit predictions differ')
    result = {'record_sha256': hashlib.sha256(raw).hexdigest(), 'device': device,
              'first_round_refitted_candidates': len(identifiers), 'maximum_mean_difference': mean_diff,
              'maximum_spread_difference': spread_diff, 'counts': dict(counts),
              'new_measurements': row['new_measurements'], 'stop_reason': row['stop_reason'],
              'covered': row['covered'], 'range_count': row['range_count']}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('record', type=Path)
    parser.add_argument('specification', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--seed', type=int, required=True)
    parser.add_argument('--device', choices=('cpu', 'cuda'), required=True)
    parser.add_argument('--repair', action='store_true')
    args = parser.parse_args()
    result = audit_record(args.record, args.specification, args.seed, args.device, args.repair)
    with args.output.open('x', encoding='utf-8') as file:
        json.dump(result, file, indent=2, allow_nan=False)
        file.write('\n')
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
