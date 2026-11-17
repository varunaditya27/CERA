#!/usr/bin/env python3
"""Independently audit Amylase repair-safeguard comparisons."""
import argparse
import csv
import gzip
import json
from collections import Counter
from pathlib import Path

from app.datasets.amylase import DATA, REFERENCE
from app.provenance.sources import validate_recorded_sources
from audit_development_repairs import audit_run, digest, read_source, require
from audit_matched_proteins import check_repair_cost, check_repair_order


def check_action_order(actions, expected, can_stop, failures):
    actual = [action['warning'] for action in actions]
    require(actual == expected[:len(actual)] and
            (len(actual) == len(expected) or (can_stop and failures >= 2)),
            'Missing or reordered repair actions')


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
    comparison = manifest.get('comparison', 'stopping')
    if comparison == 'stopping':
        seeds, methods = list(range(71, 76)), ['normal', 'continue']
    elif comparison == 'evidence':
        seeds, methods = list(range(81, 86)), ['normal', 'bypass']
    elif comparison == 'repair-terms':
        seeds, methods = list(range(91, 96)), ['normal', 'no_distance', 'no_uncertainty', 'no_diversity']
    else:
        raise ValueError('Unexpected study comparison')
    require(manifest['seeds'] == seeds and manifest['methods'] == methods
            and manifest['dataset'] == 'amylase', 'Unexpected study scope')
    require(manifest['data_sha256'] == digest(DATA.read_bytes()) and
            manifest['reference_sha256'] == digest(REFERENCE.read_bytes()) and
            manifest['specification_sha256'] == digest(Path('research/reward_spec_example.json').read_bytes()),
            'Source fingerprint mismatch')
    with (args.root / 'summary.csv').open(newline='', encoding='utf-8') as file:
        rows = list(csv.DictReader(file))
    summaries = {(int(row['seed']), row['method']): row for row in rows}
    require(len(rows) == len(summaries) == len(seeds) * len(methods), 'Missing or duplicate summaries')
    sequences, scores, train = read_source()
    counts, initials = Counter(), {}
    for seed in seeds:
        for method in methods:
            path = args.root / f'seed_{seed:02d}' / method
            status = json.loads((path / 'status.json').read_text())
            require(status['status'] == 'completed', 'Run did not complete')
            blob = (path / 'run.jsonl.gz').read_bytes()
            require(digest(blob) == status['gzip_sha256'], 'Compressed record fingerprint mismatch')
            raw = gzip.decompress(blob)
            require(digest(raw) == status['uncompressed_sha256'], 'Record fingerprint mismatch')
            events = [json.loads(line) for line in raw.splitlines()]
            setup = next(e['settings'] for e in events if e['event'] == 'method')
            removed = {'no_distance': 'distance_penalty', 'no_uncertainty': 'uncertainty_penalty',
                       'no_diversity': 'diversity_bonus'}.get(method)
            require(setup['stop_on_failed_repairs'] is (method != 'continue') and
                    setup.get('bypass_evidence_gate', False) is (method == 'bypass') and
                    setup.get('disabled_repair_terms', []) == ([removed] if removed else []) and
                    setup['cache_sha256'] == manifest['cache_sha256'], 'Study mode mismatch')
            validate_recorded_sources(setup['source_sha256'], manifest['code_sha256'])
            check_stopping(events, method != 'continue')
            spec = setup['reward_spec']
            bypassed = disabled = 0
            warnings = {(event['round'], event['type']): event['status'] for event in events
                        if event['event'] == 'warning'}
            terms = {'support_shift': 'distance_penalty', 'coverage': 'uncertainty_penalty',
                     'disagreement': 'uncertainty_penalty', 'diversity': 'diversity_bonus'}
            for event in events:
                if event['event'] != 'method':
                    continue
                actions = event['settings'].get('repair_actions')
                if actions is None:
                    continue
                round_number = event['settings']['round']
                priority = ('support_shift', 'coverage', 'disagreement', 'diversity')
                expected = [kind for kind in priority if warnings.get((round_number, kind)) == 'triggered']
                check_action_order(actions, expected, method != 'continue', event['settings']['consecutive_failures'])
                for action in actions:
                    kind = action['warning']
                    require(warnings.get((event['settings']['round'], kind)) == 'triggered', 'Action lacks warning')
                    if action['status'] == 'repair_disabled':
                        require(removed is not None and terms[kind] == removed and action['term'] == removed,
                                'Unexpected disabled repair')
                        disabled += 1
                        continue
                    require(removed is None or terms[kind] != removed, 'Disabled repair was attempted')
                    if action['status'] not in ('accepted', 'retained'):
                        continue
                    check_repair_order(spec, 'repair', action)
                    for attempt in action['attempts']:
                        check_repair_cost(spec, action['warning'], attempt)
                        require(attempt['verification']['checks']['allowed_change_and_constraints'] is True,
                                'Repair menu guard mismatch')
                    if action['status'] == 'accepted':
                        if method == 'bypass':
                            require(len(action['attempts']) == 1, 'Evidence bypass did not use first eligible proposal')
                        bypassed += not action['attempts'][-1]['verification']['accepted']
                        spec = action['specification']
            if 'accepted_without_evidence' in summaries[(seed, method)]:
                require(int(summaries[(seed, method)]['accepted_without_evidence']) == bypassed,
                        'Bypass count mismatch')
            if 'disabled_actions' in summaries[(seed, method)]:
                require(int(summaries[(seed, method)]['disabled_actions']) == disabled, 'Disabled repair count mismatch')
            initial = audit_run(events, seed, 'direct', sequences, scores, train, manifest,
                                summaries[(seed, method)], counts, bypass_evidence_gate=method == 'bypass')
            if seed in initials:
                require(initials[seed] == initial, 'Paired starts differ')
            initials[seed] = initial
    print(json.dumps(dict(counts), sort_keys=True))


if __name__ == '__main__':
    main()
