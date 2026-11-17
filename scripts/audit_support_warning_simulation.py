#!/usr/bin/env python3
"""Independently reproduce the controlled unfamiliar-candidate simulation."""
import argparse
import hashlib
import json
import math
import platform
import random
from importlib.metadata import version
from pathlib import Path

from scipy.stats import binom

from app.provenance.sources import source_hashes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report', type=Path)
    args = parser.parse_args()
    report = json.loads(args.report.read_text())
    script = Path(__file__).with_name('simulate_support_warning.py')
    if (report['seed'] != 2026111702 or report['batches_per_condition'] != 1000
            or report['python'] != platform.python_version()
            or report['versions'] != {name: version(name) for name in ('numpy', 'scipy')}
            or report['script_sha256'] != hashlib.sha256(script.read_bytes()).hexdigest()
            or report['warning_source_sha256'] != source_hashes(('warning_checks.py',))):
        raise ValueError('Simulation configuration or fingerprint mismatch')
    generator = random.Random(2026111702)
    known = [0., 1., 2., 3., 4.]
    nearest = [min(abs(x - y) for j, y in enumerate(known) if i != j) for i, x in enumerate(known)]
    threshold = sorted(nearest)[math.ceil(0.9 * len(known)) - 1]
    counts = {}
    for name, shifted, probability in (('reference', False, 0.10), ('shifted_well_covered', True, 0.10),
                                       ('shifted_poorly_covered', True, 0.50)):
        points = [float(10 + i) if shifted else 1. + (i + 1) / 100 for i in range(10)]
        distances = {f'c{i}': min(abs(point - known_point) for known_point in known)
                     for i, point in enumerate(points)}
        triggered = 0
        for _ in range(1000):
            misses = [generator.random() < probability for _ in range(10)]
            triggered += sum(distances[f'c{i}'] > threshold and misses[i] for i in range(10)) >= 3
        saved = report['conditions'][name]
        exact = float(binom.sf(2, 10, probability)) if shifted else 0.
        if (saved['shifted'] is not shifted or saved['miss_probability'] != probability or saved['batches'] != 1000
                or not math.isclose(saved['distance_threshold'], threshold, abs_tol=1e-12)
                or set(saved['distances']) != set(distances)
                or any(not math.isclose(saved['distances'][key], value, abs_tol=1e-12) for key, value in distances.items())
                or saved['triggered'] != triggered or saved['not_triggered'] != 1000 - triggered
                or saved['unavailable'] != 0
                or not math.isclose(saved['exact_trigger_probability'], exact, rel_tol=1e-12, abs_tol=1e-15)):
            raise ValueError('Condition distances, counts or analytical probability mismatch')
        counts[name] = triggered
    for name in ('shifted_well_covered', 'shifted_poorly_covered'):
        tp, fn, fp, tn = counts[name], 1000 - counts[name], counts['reference'], 1000 - counts['reference']
        expected = {'true_positive': tp, 'false_negative': fn, 'false_positive': fp, 'true_negative': tn,
                    'positive_unavailable': 0, 'negative_unavailable': 0,
                    'precision': tp / (tp + fp) if tp + fp else None,
                    'recall': tp / (tp + fn), 'false_alarm_rate': fp / (fp + tn),
                    'f1': 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else None}
        if report['comparisons'][name] != expected:
            raise ValueError('Comparison metrics mismatch')
    print(json.dumps({'checked_batches': 3000, 'triggered': counts}, sort_keys=True))


if __name__ == '__main__':
    main()
