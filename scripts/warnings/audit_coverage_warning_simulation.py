#!/usr/bin/env python3
"""Independently reproduce controlled coverage-warning simulation counts."""
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
    script = Path(__file__).with_name('simulate_coverage_warning.py')
    if (report['seed'] != 20261117 or report['windows_per_condition'] != 1000
            or report['python'] != platform.python_version()
            or report['versions'] != {name: version(name) for name in ('numpy', 'scipy')}
            or report['script_sha256'] != hashlib.sha256(script.read_bytes()).hexdigest()
            or report['warning_source_sha256'] != source_hashes(('warning_checks.py',))):
        raise ValueError('Simulation configuration or fingerprint mismatch')
    generator = random.Random(20261117)
    counts = {}
    for name, probability in (('nominal', 0.90), ('moderate', 0.80), ('severe', 0.60)):
        triggered = sum(sum(generator.random() < probability for _ in range(30)) <= 22 for _ in range(1000))
        saved = report['conditions'][name]
        if (saved['coverage_probability'] != probability or saved['windows'] != 1000
                or saved['triggered'] != triggered or saved['not_triggered'] != 1000 - triggered
                or saved['unavailable'] != 0
                or not math.isclose(saved['exact_trigger_probability'], float(binom.cdf(22, 30, probability)),
                                    rel_tol=1e-12, abs_tol=1e-15)):
            raise ValueError('Condition counts or analytical probability mismatch')
        counts[name] = triggered
    for name in ('moderate', 'severe'):
        tp, fn, fp, tn = counts[name], 1000 - counts[name], counts['nominal'], 1000 - counts['nominal']
        saved = report['comparisons'][name]
        expected = {'true_positive': tp, 'false_negative': fn, 'false_positive': fp, 'true_negative': tn,
                    'positive_unavailable': 0, 'negative_unavailable': 0,
                    'precision': tp / (tp + fp), 'recall': tp / (tp + fn),
                    'false_alarm_rate': fp / (fp + tn), 'f1': 2 * tp / (2 * tp + fp + fn)}
        if saved != expected:
            raise ValueError('Comparison metrics mismatch')
    print(json.dumps({'checked_windows': 3000, 'triggered': counts}, sort_keys=True))


if __name__ == '__main__':
    main()
