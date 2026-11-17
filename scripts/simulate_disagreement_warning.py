#!/usr/bin/env python3
"""Evaluate model-disagreement warnings on planted ranking changes."""
import argparse
import hashlib
import itertools
import json
import platform
import random
from collections import Counter
from importlib.metadata import version
from pathlib import Path

from app.provenance.sources import source_hashes
from app.rewards.warning_checks import disagreement_warning

SEED = 2026111703
CONDITIONS = ('identical', 'swapped', 'reversed')


def simulate(seed=SEED):
    generator = random.Random(seed)
    cases, counts = [], {name: Counter() for name in CONDITIONS}
    for low, high in itertools.combinations(range(10), 2):
        base = list(range(10))
        generator.shuffle(base)
        for condition in CONDITIONS:
            changed = list(base)
            if condition == 'swapped':
                a, b = base.index(low), base.index(high)
                changed[a], changed[b] = changed[b], changed[a]
            elif condition == 'reversed':
                changed = [9 - value for value in base]
            members = {str(i): [float(base[i])] * 4 + [float(changed[i])] for i in range(10)}
            means = {identifier: sum(values) / 5 for identifier, values in members.items()}
            result = disagreement_warning(means, members)
            if result['status'] not in ('triggered', 'not_triggered', 'unavailable'):
                raise ValueError('Unexpected warning status')
            counts[condition][result['status']] += 1
            cases.append({'condition': condition, 'rank_pair': [low, high], 'members': members,
                          'warning_group': result['identifiers'], 'status': result['status'], 'value': result['value']})
    conditions = {name: {'cases': sum(counts[name].values()), 'triggered': counts[name]['triggered'],
                         'not_triggered': counts[name]['not_triggered'], 'unavailable': counts[name]['unavailable']}
                  for name in CONDITIONS}
    comparisons = {}
    for name in ('swapped', 'reversed'):
        positive, negative = conditions[name], conditions['identical']
        tp, fn = positive['triggered'], positive['not_triggered']
        fp, tn = negative['triggered'], negative['not_triggered']
        comparisons[name] = {'true_positive': tp, 'false_negative': fn, 'false_positive': fp, 'true_negative': tn,
                             'positive_unavailable': positive['unavailable'], 'negative_unavailable': negative['unavailable'],
                             'precision': tp / (tp + fp) if tp + fp else None,
                             'recall': tp / (tp + fn) if tp + fn else None,
                             'false_alarm_rate': fp / (fp + tn) if fp + tn else None,
                             'f1': 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else None}
    return {'seed': seed, 'conditions': conditions, 'comparisons': comparisons, 'cases': cases}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    result = {'scope': 'synthetic planted ranking changes; not biological validation',
              'python': platform.python_version(), 'versions': {name: version(name) for name in ('numpy', 'scipy')},
              'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'warning_source_sha256': source_hashes(('warning_checks.py',)), **simulate()}
    with args.output.open('x', encoding='utf-8') as file:
        json.dump(result, file, indent=2, allow_nan=False)
        file.write('\n')


if __name__ == '__main__':
    main()
