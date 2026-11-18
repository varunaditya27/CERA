#!/usr/bin/env python3
"""Reproduce each recorded mixed-predictor round from revealed measurements."""
import argparse
import gzip
import hashlib
import json
import math
from pathlib import Path
import tempfile

from app.experiments.hybrid_predictor import fit_hybrid_group
from app.experiments.predictor_group import predict_group
from app.features.amylase_representations import load_verified_representations
from audit_hybrid_pilot import audit_record


def audit_rounds(events, vectors, device):
    setup = next(e['settings'] for e in events if e['event'] == 'method')
    known = dict(events[0]['initial'])
    fit = None
    maxima = {'mean': 0.0, 'spread': 0.0}
    rounds = 0
    for event in events:
        if event['event'] == 'method' and 'hybrid_fit' in event['settings']:
            if fit is not None:
                raise ValueError('Missing selection for predictor fit')
            fit = event['settings']
        elif event['event'] == 'selection':
            if fit is None or set(fit['fitting_ids']) != set(known) - set(setup['reserved_ids']):
                raise ValueError('Predictor fit does not match revealed measurements')
            models, penalty, metadata = fit_hybrid_group(
                vectors, known, fit['fitting_ids'], setup['reserved_ids'], setup['cv_seed'],
                fit['member_seeds'], device)
            if (penalty != fit['penalty'] or metadata['training_ids'] != fit['hybrid_fit']['training_ids']
                    or metadata['validation_ids'] != fit['hybrid_fit']['validation_ids']):
                raise ValueError('Refit roles or penalty differ')
            recorded = event['prediction_ranges']
            ids = sorted(recorded)
            means, spreads = predict_group(models, vectors, ids)
            for name, values in [('mean', means), ('spread', spreads)]:
                differences = [abs(float(value) - recorded[identifier][name]) for identifier, value in zip(ids, values)]
                if len(differences) != len(ids) or not differences or not all(map(math.isfinite, differences)):
                    raise ValueError('Invalid refit predictions')
                difference = max(differences)
                maxima[name] = max(maxima[name], difference)
                if difference > 1e-5:
                    raise ValueError(f'Refit {name} differs in round {rounds + 1}: {difference}')
            rounds += 1
            fit = None
        elif event['event'] == 'reveal':
            if set(known) & set(event['measurements']):
                raise ValueError('Measurement repeated')
            known.update(event['measurements'])
    if fit is not None or rounds != 10:
        raise ValueError('Expected ten complete predictor rounds')
    return {'rounds': rounds, 'maximum_differences': maxima}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    parser.add_argument('specification', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('Output already exists')
    vectors = load_verified_representations()
    results = []
    for seed in range(191, 201):
        raw = gzip.decompress((args.directory / f'{seed}_mixed' / 'run.jsonl.gz').read_bytes())
        events = [json.loads(line) for line in raw.splitlines()]
        with tempfile.TemporaryDirectory() as temporary:
            record = Path(temporary) / 'run.jsonl'
            record.write_bytes(raw)
            audit_record(record, args.specification, seed, 'cuda', False)
        result = audit_rounds(events, vectors, 'cuda')
        results.append({'seed': seed, 'record_sha256': hashlib.sha256(raw).hexdigest(), **result})
        print(f"Seed {seed}: {result['rounds']} rounds reproduced", flush=True)
    with args.output.open('x', encoding='utf-8') as file:
        json.dump({'device': 'cuda', 'runs': results}, file, indent=2, allow_nan=False)
        file.write('\n')


if __name__ == '__main__':
    main()
