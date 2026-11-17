#!/usr/bin/env python3
"""Exploratory paired analysis of previously reported search outcomes."""
import argparse
import hashlib
import itertools
import json
from importlib.metadata import version
from pathlib import Path

import numpy as np
from scipy.stats import rankdata

SEEDS = range(51, 61)
GROUPS = ('ired', 'hydro-P06241', 'hydro-P01053', 'hydro-P0A9X9')
METHODS = ('repair', 'gemini_repair')


def signed_rank(differences):
    nonzero = np.asarray([x for x in differences if abs(x) > 1e-12], dtype=float)
    if not len(nonzero):
        return None
    ranks = rankdata(np.abs(nonzero), method='average')
    observed = abs(float(np.dot(np.sign(nonzero), ranks)))
    values = [abs(float(np.dot(signs, ranks))) for signs in itertools.product((-1, 1), repeat=len(ranks))]
    return sum(value >= observed - 1e-12 for value in values) / len(values)


def analyze(report):
    groups = report['groups']
    if len(groups) != len(GROUPS) or {g['dataset'] for g in groups} != set(GROUPS):
        raise ValueError('Unexpected study groups')
    groups = {g['dataset']: g for g in groups}
    rng = np.random.default_rng(20261117)
    results = []
    for dataset in GROUPS:
        records = {}
        for row in groups[dataset]['summaries']:
            if row['method'] not in ('fixed', *METHODS):
                continue
            key = (row['seed'], row['method'])
            if key in records or row['status'] != 'completed':
                raise ValueError('Duplicate or incomplete record')
            records[key] = row
        if set(records) != {(seed, method) for seed in SEEDS for method in ('fixed', *METHODS)}:
            raise ValueError('Missing or unexpected seed')
        for method in METHODS:
            pairs = []
            for seed in SEEDS:
                base, repair = records[seed, 'fixed'], records[seed, method]
                values = [base['best_observed'], repair['best_observed']]
                if not np.isfinite(values).all():
                    raise ValueError('Nonfinite score')
                pairs.append({'seed': seed, 'difference': values[1] - values[0],
                              'fixed_measurements': base['new_measurements'],
                              'repair_measurements': repair['new_measurements']})
            differences = np.array([pair['difference'] for pair in pairs])
            sampled = differences[rng.integers(0, len(differences), size=(20000, len(differences)))].mean(axis=1)
            results.append({'dataset': dataset, 'method': method, 'pairs': pairs,
                            'mean_difference': float(differences.mean()),
                            'percentile_interval_95': np.quantile(sampled, [0.025, 0.975]).tolist(),
                            'signed_rank_p': signed_rank(differences), 'holm_p': None})
    available = sorted((r['signed_rank_p'], i) for i, r in enumerate(results) if r['signed_rank_p'] is not None)
    previous = 0.0
    for rank, (p, index) in enumerate(available):
        previous = max(previous, min(1.0, p * (len(available) - rank)))
        results[index]['holm_p'] = previous
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    raw = args.report.read_bytes()
    output = {'scope': 'post-result exploratory; fixed datasets and repeated starts',
              'input_sha256': hashlib.sha256(raw).hexdigest(),
              'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'versions': {name: version(name) for name in ('numpy', 'scipy')},
              'random_seed': 20261117, 'bootstrap_resamples': 20000,
              'comparisons': analyze(json.loads(raw))}
    with args.output.open('x', encoding='utf-8') as file:
        json.dump(output, file, indent=2, allow_nan=False)
        file.write('\n')


if __name__ == '__main__':
    main()
