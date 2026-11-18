#!/usr/bin/env python3
"""Evaluate the unfamiliar-candidate warning on controlled synthetic batches."""
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
from app.rewards.warning_checks import distance_snapshot, support_warning

SEED = 2026111702
BATCHES = 1000
CONDITIONS = (('reference', False, 0.10), ('shifted_well_covered', True, 0.10),
              ('shifted_poorly_covered', True, 0.50))


def exact_shifted_probability(miss_probability):
    if not 0 <= miss_probability <= 1:
        raise ValueError('Probability outside [0, 1]')
    return math.fsum(math.comb(10, k) * miss_probability ** k * (1 - miss_probability) ** (10 - k)
                     for k in range(3, 11))


def simulate(seed=SEED, batches=BATCHES):
    if not isinstance(batches, int) or isinstance(batches, bool) or batches < 1:
        raise ValueError('Invalid batch count')
    known = [f'k{i}' for i in range(5)]
    ids = [f'c{i}' for i in range(10)]
    generator = random.Random(seed)
    conditions = {}
    for name, shifted, miss_probability in CONDITIONS:
        vectors = {identifier: [float(i)] for i, identifier in enumerate(known)}
        vectors.update({identifier: [float(10 + i) if shifted else 1. + (i + 1) / 100]
                        for i, identifier in enumerate(ids)})
        snapshot = distance_snapshot(known, ids, vectors)
        ranges = {identifier: {'lower': 0., 'upper': 1.} for identifier in ids}
        counts = Counter()
        for _ in range(batches):
            measurements = {identifier: (2. if generator.random() < miss_probability else 0.5) for identifier in ids}
            status = support_warning(snapshot, ranges, measurements)['status']
            if status not in ('triggered', 'not_triggered', 'unavailable'):
                raise ValueError('Unexpected warning status')
            counts[status] += 1
        conditions[name] = {'shifted': shifted, 'miss_probability': miss_probability, 'batches': batches,
                            'distance_threshold': snapshot['threshold'], 'distances': snapshot['distances'],
                            'triggered': counts['triggered'], 'not_triggered': counts['not_triggered'],
                            'unavailable': counts['unavailable'], 'exact_trigger_probability':
                            exact_shifted_probability(miss_probability) if shifted else 0.}
    comparisons = {}
    for name in ('shifted_well_covered', 'shifted_poorly_covered'):
        positive, negative = conditions[name], conditions['reference']
        tp, fn = positive['triggered'], positive['not_triggered']
        fp, tn = negative['triggered'], negative['not_triggered']
        comparisons[name] = {'true_positive': tp, 'false_negative': fn, 'false_positive': fp, 'true_negative': tn,
                             'positive_unavailable': positive['unavailable'], 'negative_unavailable': negative['unavailable'],
                             'precision': tp / (tp + fp) if tp + fp else None,
                             'recall': tp / (tp + fn) if tp + fn else None,
                             'false_alarm_rate': fp / (fp + tn) if fp + tn else None,
                             'f1': 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else None}
    return {'seed': seed, 'batches_per_condition': batches, 'conditions': conditions, 'comparisons': comparisons}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    result = {'scope': 'synthetic constructed shifts; not biological validation',
              'python': platform.python_version(), 'versions': {name: version(name) for name in ('numpy', 'scipy')},
              'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'warning_source_sha256': source_hashes(('warning_checks.py',)), **simulate()}
    with args.output.open('x', encoding='utf-8') as file:
        json.dump(result, file, indent=2, allow_nan=False)
        file.write('\n')


if __name__ == '__main__':
    main()
