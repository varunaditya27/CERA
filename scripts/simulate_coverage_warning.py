#!/usr/bin/env python3
"""Evaluate the coverage warning on controlled independent synthetic windows."""
import argparse
import hashlib
import json
import math
import platform
import random
from collections import Counter
from importlib.metadata import version
from pathlib import Path

from app.provenance.sources import source_hashes
from app.rewards.warning_checks import coverage_warning

SEED = 20261117
WINDOWS = 1000
CONDITIONS = (('nominal', 0.90), ('moderate', 0.80), ('severe', 0.60))


def exact_trigger_probability(probability):
    if not 0 <= probability <= 1:
        raise ValueError('Probability outside [0, 1]')
    return math.fsum(math.comb(30, k) * probability ** k * (1 - probability) ** (30 - k)
                     for k in range(23))


def simulate(seed=SEED, windows=WINDOWS):
    if not isinstance(windows, int) or isinstance(windows, bool) or windows < 1:
        raise ValueError('Invalid window count')
    generator = random.Random(seed)
    conditions = {}
    for name, probability in CONDITIONS:
        counts = Counter()
        for _ in range(windows):
            history = [(str(i), generator.random() < probability) for i in range(30)]
            status = coverage_warning(history)['status']
            if status not in ('triggered', 'not_triggered', 'unavailable'):
                raise ValueError('Unexpected warning status')
            counts[status] += 1
        conditions[name] = {'coverage_probability': probability, 'windows': windows,
                            'triggered': counts['triggered'], 'not_triggered': counts['not_triggered'],
                            'unavailable': counts['unavailable'],
                            'exact_trigger_probability': exact_trigger_probability(probability)}
    comparisons = {}
    for name in ('moderate', 'severe'):
        positive, negative = conditions[name], conditions['nominal']
        tp, fn = positive['triggered'], positive['not_triggered']
        fp, tn = negative['triggered'], negative['not_triggered']
        precision = tp / (tp + fp) if tp + fp else None
        recall = tp / (tp + fn) if tp + fn else None
        comparisons[name] = {'true_positive': tp, 'false_negative': fn, 'false_positive': fp, 'true_negative': tn,
                             'positive_unavailable': positive['unavailable'], 'negative_unavailable': negative['unavailable'],
                             'precision': precision, 'recall': recall,
                             'false_alarm_rate': fp / (fp + tn) if fp + tn else None,
                             'f1': 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else None}
    return {'seed': seed, 'windows_per_condition': windows, 'conditions': conditions, 'comparisons': comparisons}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    result = {'scope': 'synthetic independent windows; not biological validation',
              'python': platform.python_version(), 'versions': {name: version(name) for name in ('numpy', 'scipy')},
              'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'warning_source_sha256': source_hashes(('warning_checks.py',)), **simulate()}
    with args.output.open('x', encoding='utf-8') as file:
        json.dump(result, file, indent=2, allow_nan=False)
        file.write('\n')


if __name__ == '__main__':
    main()
