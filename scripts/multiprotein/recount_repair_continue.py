#!/usr/bin/env python3
"""Recompute each run's best score and measurement count from the raw records, without the project's evaluator."""
import argparse
import gzip
import json
from pathlib import Path


def best_and_count(lines):
    events = [json.loads(line) for line in lines]
    best = max(events[0]['initial'].values())
    count = 0
    for event in events[1:]:
        if event['event'] == 'reveal':
            count += len(event['measurements'])
            best = max(best, *event['measurements'].values())
    return best, count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('comparison', type=Path, help='Report written by compare_repair_continue')
    parser.add_argument('roots', type=Path, nargs='+', help='The new study directories, in the report order')
    args = parser.parse_args()
    report = json.loads(args.comparison.read_text())
    checked = 0
    for group, root in zip(report['groups'], args.roots):
        for row in group['rows']:
            for method, key in (('repair_continue', 'continue'), ('repair', 'repair')):
                path = root / f"seed_{row['seed']:02d}" / method / 'run.jsonl.gz'
                if not path.exists():
                    continue
                best, count = best_and_count(gzip.decompress(path.read_bytes()).decode().splitlines())
                if best != row[f'{key}_best'] or count != row[f'{key}_measurements']:
                    raise ValueError(f'Recount differs for {root.name} seed {row["seed"]} {method}')
                checked += 1
    print(json.dumps({'recounted_runs': checked}))


if __name__ == '__main__':
    main()
