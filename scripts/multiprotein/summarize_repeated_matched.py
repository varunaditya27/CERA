#!/usr/bin/env python3
"""Summarize completed repeated runs without padding early stops."""
import argparse
import collections
import csv
import hashlib
import json
import statistics
from pathlib import Path


def write_csv(path, rows):
    with path.open('x', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    args = parser.parse_args()
    source = args.root / 'summary.csv'
    with source.open(newline='', encoding='utf-8') as file:
        rows = list(csv.DictReader(file))
    if len({(row['seed'], row['method']) for row in rows}) != len(rows):
        raise ValueError('Duplicate seed and method')
    grouped = collections.defaultdict(list)
    lookup = {}
    for row in rows:
        grouped[row['method']].append(row)
        lookup[(row['seed'], row['method'])] = row
    method_rows = []
    for method, group in grouped.items():
        completed = [row for row in group if row['status'] == 'completed']
        values = [float(row['best_observed']) for row in completed]
        counts = [int(row['new_measurements']) for row in completed]
        ranges = [row for row in completed if int(row['range_count'])]
        method_rows.append({'method': method, 'requested': len(group), 'completed': len(completed),
                            'median_best': statistics.median(values) if values else None,
                            'min_best': min(values) if values else None, 'max_best': max(values) if values else None,
                            'min_new': min(counts) if counts else None, 'median_new': statistics.median(counts) if counts else None,
                            'max_new': max(counts) if counts else None,
                            'pooled_covered': sum(int(row['covered']) for row in ranges) if ranges else None,
                            'pooled_range_count': sum(int(row['range_count']) for row in ranges),
                            'median_mean_width': statistics.median(float(row['mean_range_width']) for row in ranges) if ranges else None,
                            'stops': json.dumps(dict(collections.Counter(row['stop_reason'] for row in completed)), sort_keys=True)})
    paired = []
    for seed in sorted({row['seed'] for row in rows}, key=int):
        for left, right in (('repair', 'fixed'), ('gemini_repair', 'repair')):
            a, b = lookup.get((seed, left)), lookup.get((seed, right))
            available = a and b and a['status'] == b['status'] == 'completed'
            paired.append({'seed': seed, 'left': left, 'right': right, 'available': bool(available),
                           'best_difference': float(a['best_observed']) - float(b['best_observed']) if available else None,
                           'left_new': int(a['new_measurements']) if available else None,
                           'right_new': int(b['new_measurements']) if available else None})
    write_csv(args.root / 'method_summary.csv', method_rows)
    write_csv(args.root / 'paired_differences.csv', paired)
    manifest = {'summary_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    with (args.root / 'aggregate_fingerprints.json').open('x', encoding='utf-8') as file:
        json.dump(manifest, file, indent=2)
        file.write('\n')
    print(json.dumps({'methods': len(method_rows), 'paired_rows': len(paired)}))


if __name__ == '__main__':
    main()
