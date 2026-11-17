#!/usr/bin/env python3
"""Independently audit the Amylase repair-stopping comparison."""
import argparse
import csv
import gzip
import json
from collections import Counter
from pathlib import Path

from app.datasets.amylase import DATA, REFERENCE
from app.provenance.sources import validate_recorded_sources
from audit_development_repairs import audit_run, digest, read_source, require


def check_stopping(events, normal):
    failures = 0
    for index, event in enumerate(events):
        if event['event'] == 'stop' and event['stop_reason'] == 'failed_repairs':
            require(normal and failures >= 2, 'Unexpected failed-repair stop')
        if event['event'] != 'method' or 'repair_actions' not in event['settings']:
            continue
        settings = event['settings']
        for action in settings['repair_actions']:
            if action['status'] == 'accepted':
                failures = 0
            elif action['status'] == 'retained':
                failures += 1
            else:
                continue
            require(action['consecutive_failures'] == failures, 'Failure count mismatch')
        require(settings['consecutive_failures'] == failures, 'Recorded failure count mismatch')
        if normal and failures >= 2:
            require(index + 1 < len(events) and events[index + 1]['event'] == 'stop'
                    and events[index + 1]['stop_reason'] == 'failed_repairs', 'Missing required stop')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    args = parser.parse_args()
    manifest = json.loads((args.root / 'manifest.json').read_text())
    require(manifest['seeds'] == list(range(71, 76)) and manifest['methods'] == ['normal', 'continue']
            and manifest['dataset'] == 'amylase', 'Unexpected study scope')
    require(manifest['data_sha256'] == digest(DATA.read_bytes()) and
            manifest['reference_sha256'] == digest(REFERENCE.read_bytes()) and
            manifest['specification_sha256'] == digest(Path('research/reward_spec_example.json').read_bytes()),
            'Source fingerprint mismatch')
    with (args.root / 'summary.csv').open(newline='', encoding='utf-8') as file:
        rows = list(csv.DictReader(file))
    summaries = {(int(row['seed']), row['method']): row for row in rows}
    require(len(rows) == len(summaries) == 10, 'Missing or duplicate summaries')
    sequences, scores, train = read_source()
    counts, initials = Counter(), {}
    for seed in range(71, 76):
        for method in ('normal', 'continue'):
            path = args.root / f'seed_{seed:02d}' / method
            status = json.loads((path / 'status.json').read_text())
            require(status['status'] == 'completed', 'Run did not complete')
            blob = (path / 'run.jsonl.gz').read_bytes()
            require(digest(blob) == status['gzip_sha256'], 'Compressed record fingerprint mismatch')
            raw = gzip.decompress(blob)
            require(digest(raw) == status['uncompressed_sha256'], 'Record fingerprint mismatch')
            events = [json.loads(line) for line in raw.splitlines()]
            setup = next(e['settings'] for e in events if e['event'] == 'method')
            require(setup['stop_on_failed_repairs'] is (method == 'normal') and
                    setup['cache_sha256'] == manifest['cache_sha256'], 'Study mode mismatch')
            validate_recorded_sources(setup['source_sha256'], manifest['code_sha256'])
            check_stopping(events, method == 'normal')
            initial = audit_run(events, seed, 'direct', sequences, scores, train, manifest,
                                summaries[(seed, method)], counts)
            if seed in initials:
                require(initials[seed] == initial, 'Paired starts differ')
            initials[seed] = initial
    print(json.dumps(dict(counts), sort_keys=True))


if __name__ == '__main__':
    main()
