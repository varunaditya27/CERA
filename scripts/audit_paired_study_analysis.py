#!/usr/bin/env python3
"""Independently check a saved exploratory paired analysis."""
import argparse
import hashlib
import json
from importlib.metadata import version
from pathlib import Path

import numpy as np
from scipy.stats import PermutationMethod, wilcoxon


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('analysis', type=Path)
    args = parser.parse_args()
    raw = args.input.read_bytes()
    source = json.loads(raw)
    saved = json.loads(args.analysis.read_text())
    script = Path(__file__).with_name('analyze_paired_study.py')
    if (saved['input_sha256'] != hashlib.sha256(raw).hexdigest()
            or saved['script_sha256'] != hashlib.sha256(script.read_bytes()).hexdigest()
            or saved['versions'] != {x: version(x) for x in ('numpy', 'scipy')}
            or saved['random_seed'] != 20261117 or saved['bootstrap_resamples'] != 20000):
        raise ValueError('Fingerprint or configuration mismatch')
    groups = {g['dataset']: g for g in source['groups']}
    expected = [(g, m) for g in ('ired', 'hydro-P06241', 'hydro-P01053', 'hydro-P0A9X9')
                for m in ('repair', 'gemini_repair')]
    if [(c['dataset'], c['method']) for c in saved['comparisons']] != expected:
        raise ValueError('Comparison identity mismatch')
    rng = np.random.default_rng(20261117)
    probabilities = []
    for result in saved['comparisons']:
        rows = groups[result['dataset']]['summaries']
        differences = []
        for pair in result['pairs']:
            matched = [r for r in rows if r['seed'] == pair['seed'] and r['method'] in ('fixed', result['method'])]
            if len(matched) != 2 or len({r['method'] for r in matched}) != 2:
                raise ValueError('Pair mismatch')
            fixed = next(r for r in matched if r['method'] == 'fixed')
            repair = next(r for r in matched if r['method'] == result['method'])
            difference = repair['best_observed'] - fixed['best_observed']
            if (pair['difference'] != difference or pair['fixed_measurements'] != fixed['new_measurements']
                    or pair['repair_measurements'] != repair['new_measurements']):
                raise ValueError('Saved observation mismatch')
            differences.append(difference)
        if [p['seed'] for p in result['pairs']] != list(range(51, 61)):
            raise ValueError('Seed mismatch')
        differences = np.asarray(differences)
        indices = rng.integers(0, 10, size=(20000, 10))
        means = np.mean(differences[indices], axis=1)
        interval = np.quantile(means, [0.025, 0.975]).tolist()
        if result['mean_difference'] != float(np.mean(differences)) or result['percentile_interval_95'] != interval:
            raise ValueError('Bootstrap result mismatch')
        nonzero = differences[np.abs(differences) > 1e-12]
        p = (None if not len(nonzero) else 1.0 if len(nonzero) == 1 else
             float(wilcoxon(nonzero, method=PermutationMethod(n_resamples=2 ** len(nonzero))).pvalue))
        if result['signed_rank_p'] != p:
            raise ValueError('Signed-rank result mismatch')
        probabilities.append(p)
    ordered = sorted((p, i) for i, p in enumerate(probabilities) if p is not None)
    adjusted = [None] * len(probabilities)
    for rank, (p, index) in enumerate(ordered):
        adjusted[index] = min(1.0, max((len(ordered) - j) * v for j, (v, _) in enumerate(ordered[:rank + 1])))
    if [r['holm_p'] for r in saved['comparisons']] != adjusted:
        raise ValueError('Multiple-comparison adjustment mismatch')
    print(json.dumps({'checked_comparisons': len(expected), 'checked_pairs': len(expected) * 10,
                      'signed_rank_checks': len(ordered)}, sort_keys=True))


if __name__ == '__main__':
    main()
