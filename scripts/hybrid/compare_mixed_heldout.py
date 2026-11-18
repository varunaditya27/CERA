#!/usr/bin/env python3
"""Compare matched, already-evaluated held-out prediction runs."""
import argparse
import hashlib
import json
from pathlib import Path
from statistics import median


def compare(mixed_predictions, ridge_predictions, mixed_eval, ridge_eval):
    results = []
    groups = [x['groups'] for x in (mixed_predictions, ridge_predictions, mixed_eval, ridge_eval)]
    if any(len(g) != 4 for g in groups):
        raise ValueError('Expected four protein groups')
    for mixed, ridge, me, re in zip(*groups):
        if len({g['dataset'] for g in (mixed, ridge, me, re)}) != 1:
            raise ValueError('Dataset mismatch')
        if any(len(g['runs']) != 10 for g in (mixed, ridge, me, re)):
            raise ValueError('Expected ten matched runs')
        differences = []
        for mp, rp, mr, rr in zip(mixed['runs'], ridge['runs'], me['runs'], re['runs']):
            if (any(mp[k] != rp[k] for k in ('seed', 'initial_ids', 'reserved_ids', 'member_seeds'))
                    or mp['seed'] != mr['seed'] or mp['seed'] != rr['seed']
                    or [p[0] for p in mp['predictions']] != [p[0] for p in rp['predictions']]
                    or mr['n'] != rr['n'] or mr['n'] != len(mp['predictions'])):
                raise ValueError('Matched examples or evaluations differ')
            differences.append({'seed': mp['seed'],
                                'spearman': None if mr['spearman'] is None or rr['spearman'] is None else mr['spearman'] - rr['spearman'],
                                'mae': mr['mean_absolute_error'] - rr['mean_absolute_error'],
                                'coverage': mr['covered'] / mr['n'] - rr['covered'] / rr['n']})
        results.append({'dataset': mixed['dataset'], 'runs': differences,
                        'median_paired_difference': {key: median([r[key] for r in differences if r[key] is not None])
                                                     if any(r[key] is not None for r in differences) else None
                                                     for key in ('spearman', 'mae', 'coverage')}})
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mixed_predictions', type=Path)
    parser.add_argument('ridge_predictions', type=Path)
    parser.add_argument('mixed_evaluation', type=Path)
    parser.add_argument('ridge_evaluation', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    paths = [args.mixed_predictions, args.ridge_predictions, args.mixed_evaluation, args.ridge_evaluation]
    raw = [p.read_bytes() for p in paths]
    data = [json.loads(b) for b in raw]
    hashes = [hashlib.sha256(b).hexdigest() for b in raw]
    if data[2]['predictions_sha256'] != hashes[0] or data[3]['predictions_sha256'] != hashes[1]:
        raise ValueError('Evaluation does not match prediction file')
    result = {'input_sha256': hashes, 'groups': compare(*data)}
    with args.output.open('x', encoding='utf-8') as file:
        json.dump(result, file, indent=2, allow_nan=False)
        file.write('\n')


if __name__ == '__main__':
    main()
