#!/usr/bin/env python3
"""Summarize the terminal Hydro low-fitness-start evaluation."""
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from statistics import median

from app.experiments.repeated_runs import METHODS

DATASETS = ('hydro-P06241', 'hydro-P01053', 'hydro-P0A9X9')


def summarize(report):
    groups = report['groups']
    if report['scope'] != 'hydro_low_fitness' or {g['dataset'] for g in groups} != set(DATASETS) or len(groups) != 3:
        raise ValueError('Unexpected study scope')
    outputs = []
    for group in groups:
        rows = group['summaries']
        keys = {(r['seed'], r['method']) for r in rows}
        if (len(rows) != 90 or keys != {(s, m) for s in range(141, 151) for m in METHODS}
                or any(r['status'] != 'completed' for r in rows)):
            raise ValueError('Study has missing, repeated or failed runs')
        methods = []
        fixed = {r['seed']: r for r in rows if r['method'] == 'fixed'}
        for method in METHODS:
            runs = [r for r in rows if r['method'] == method]
            counts = [r['new_measurements'] for r in runs]
            if any(sum(r['selected_split_counts'].values()) != r['new_measurements'] for r in runs):
                raise ValueError('Split counts do not match measurement counts')
            differences = [r['best_observed'] - fixed[r['seed']]['best_observed'] for r in runs]
            methods.append({'method': method, 'median_best': median(r['best_observed'] for r in runs),
                            'new_measurements': {'median': median(counts), 'min': min(counts), 'max': max(counts)},
                            'stop_reasons': dict(sorted(Counter(r['stop_reason'] for r in runs).items())),
                            'selected_train': sum(r['selected_split_counts']['train'] for r in runs),
                            'selected_test': sum(r['selected_split_counts']['test'] for r in runs),
                            'higher_equal_lower_vs_fixed': [sum(d > 1e-12 for d in differences),
                                                            sum(abs(d) <= 1e-12 for d in differences),
                                                            sum(d < -1e-12 for d in differences)],
                            'covered': (sum(r['covered'] for r in runs if r['covered'] is not None)
                                        if any(r['covered'] is not None for r in runs) else None),
                            'range_count': sum(r['range_count'] for r in runs),
                            'repairs_accepted': sum(r['repairs_accepted'] for r in runs),
                            'advice_gemini': sum(r['advice_gemini'] for r in runs),
                            'advice_fallback': sum(r['advice_fallback'] for r in runs),
                            'advice_request_attempts': sum(r['advice_request_attempts'] for r in runs),
                            'advice_reported_tokens': sum(r['advice_reported_tokens'] for r in runs)})
        outputs.append({'dataset': group['dataset'], 'methods': methods})
    return outputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    raw = args.report.read_bytes()
    output = {'input_sha256': hashlib.sha256(raw).hexdigest(),
              'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'groups': summarize(json.loads(raw))}
    with args.output.open('x', encoding='utf-8') as file:
        json.dump(output, file, indent=2, allow_nan=False)
        file.write('\n')


if __name__ == '__main__':
    main()
