#!/usr/bin/env python3
"""Independently reproduce planted model-ranking warning cases."""
import argparse
import hashlib
import itertools
import json
import math
import platform
import random
from collections import Counter
from importlib.metadata import version
from pathlib import Path

from app.provenance.sources import source_hashes


def rank(values):
    return [1 + sum(other < value for other in values) + (sum(other == value for other in values) - 1) / 2
            for value in values]


def correlation(left, right):
    left, right = rank(left), rank(right)
    lm, rm = sum(left) / len(left), sum(right) / len(right)
    numerator = sum((a - lm) * (b - rm) for a, b in zip(left, right))
    denominator = math.sqrt(sum((a - lm) ** 2 for a in left) * sum((b - rm) ** 2 for b in right))
    return numerator / denominator


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report', type=Path)
    args = parser.parse_args()
    report = json.loads(args.report.read_text())
    script = Path(__file__).with_name('simulate_disagreement_warning.py')
    if (report['seed'] != 2026111703 or report['python'] != platform.python_version()
            or report['versions'] != {name: version(name) for name in ('numpy', 'scipy')}
            or report['script_sha256'] != hashlib.sha256(script.read_bytes()).hexdigest()
            or report['warning_source_sha256'] != source_hashes(('warning_checks.py',))):
        raise ValueError('Simulation configuration or fingerprint mismatch')
    if len(report['cases']) != 135:
        raise ValueError('Unexpected case count')
    generator = random.Random(2026111703)
    cases = iter(report['cases'])
    counts = {name: Counter() for name in ('identical', 'swapped', 'reversed')}
    for low, high in itertools.combinations(range(10), 2):
        base = list(range(10))
        generator.shuffle(base)
        for condition in counts:
            changed = list(base)
            if condition == 'swapped':
                a, b = base.index(low), base.index(high)
                changed[a], changed[b] = changed[b], changed[a]
            elif condition == 'reversed':
                changed = [9 - value for value in base]
            members = {str(i): [float(base[i])] * 4 + [float(changed[i])] for i in range(10)}
            means = {identifier: sum(values) / 5 for identifier, values in members.items()}
            group = sorted(means, key=lambda identifier: (-means[identifier], identifier))
            columns = [[members[identifier][j] for identifier in group] for j in range(5)]
            value = sum(correlation(columns[a], columns[b]) for a, b in itertools.combinations(range(5), 2)) / 10
            status = 'triggered' if value < 0.5 else 'not_triggered'
            saved = next(cases)
            if (saved['condition'] != condition or saved['rank_pair'] != [low, high] or saved['members'] != members
                    or saved['warning_group'] != group or saved['status'] != status
                    or not math.isclose(saved['value'], value, rel_tol=1e-12, abs_tol=1e-12)):
                raise ValueError('Planted case or independently calculated warning mismatch')
            counts[condition][status] += 1
    for name, group in counts.items():
        expected = {'cases': 45, 'triggered': group['triggered'], 'not_triggered': group['not_triggered'],
                    'unavailable': 0}
        if report['conditions'][name] != expected:
            raise ValueError('Condition counts mismatch')
    for name in ('swapped', 'reversed'):
        tp, fn = counts[name]['triggered'], counts[name]['not_triggered']
        fp, tn = counts['identical']['triggered'], counts['identical']['not_triggered']
        expected = {'true_positive': tp, 'false_negative': fn, 'false_positive': fp, 'true_negative': tn,
                    'positive_unavailable': 0, 'negative_unavailable': 0,
                    'precision': tp / (tp + fp) if tp + fp else None,
                    'recall': tp / (tp + fn) if tp + fn else None,
                    'false_alarm_rate': fp / (fp + tn) if fp + tn else None,
                    'f1': 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else None}
        if report['comparisons'][name] != expected:
            raise ValueError('Comparison metrics mismatch')
    print(json.dumps({'checked_cases': 135, 'triggered': {name: count['triggered'] for name, count in counts.items()}},
                     sort_keys=True))


if __name__ == '__main__':
    main()
