#!/usr/bin/env python3
"""Recheck the saved repair diagnosis against the compressed event records."""
import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

from app.analysis.multiprotein_evaluation import terminal_statuses, verified_record
from app.analysis.study_protocol import validate_hydro_low_fitness


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('diagnosis', type=Path)
    parser.add_argument('report', type=Path)
    parser.add_argument('roots', nargs=3, type=Path)
    args = parser.parse_args()
    diagnosis = json.loads(args.diagnosis.read_text())
    script = Path(__file__).with_name('diagnose_hydro_repairs.py')
    if (diagnosis['report_sha256'] != hashlib.sha256(args.report.read_bytes()).hexdigest()
            or diagnosis['script_sha256'] != hashlib.sha256(script.read_bytes()).hexdigest()):
        raise ValueError('Diagnosis fingerprint mismatch')
    groups = {group['dataset']: group for group in diagnosis['groups']}
    manifests = [json.loads((root / 'manifest.json').read_text()) for root in args.roots]
    validate_hydro_low_fitness(manifests)
    checked = proposals = 0
    for root, manifest in zip(args.roots, manifests):
        group = groups.pop(manifest['dataset'])
        statuses = terminal_statuses(root, manifest)
        runs = {(r['seed'], r['method']): r for r in group['runs']}
        if len(group['runs']) != 20 or set(runs) != {(s, m) for s in range(141, 151) for m in ('repair', 'gemini_repair')}:
            raise ValueError('Run list mismatch')
        by_method = defaultdict(list)
        for (seed, method), saved in runs.items():
            status = statuses[seed, method]
            raw = verified_record(root / f'seed_{seed:02d}' / method / 'run.jsonl.gz', status)
            if status['status'] != 'completed' or saved['record_sha256'] != status['uncompressed_sha256']:
                raise ValueError('Record fingerprint mismatch')
            actions, failures, attempts = Counter(), Counter(), Counter()
            checks = defaultdict(Counter)
            accepted = empty = 0
            last_failed, stop = [], None
            for line in raw.splitlines():
                event = json.loads(line)
                if event['event'] in ('reveal', 'stop'):
                    stop = event['stop_reason']
                if event['event'] != 'method' or 'repair_actions' not in event['settings']:
                    continue
                number = event['settings']['round']
                for action in event['settings']['repair_actions']:
                    warning, state = action['warning'], action['status']
                    actions[f'{warning}:{state}'] += 1
                    if state not in ('accepted', 'retained'):
                        continue
                    options = action['attempts']
                    empty += not options
                    attempts[warning] += len(options)
                    for item in options:
                        for key, value in item['verification']['checks'].items():
                            if value is False:
                                checks[warning][key + ':false'] += 1
                            elif value is None:
                                checks[warning][key + ':unavailable'] += 1
                    if state == 'accepted':
                        accepted += 1
                        last_failed = []
                    else:
                        failures[warning] += 1
                        last_failed.append({'round': number, 'warning': warning, 'attempts': len(options)})
            final = last_failed[-2:] if stop == 'failed_repairs' else []
            expected = {'stop_reason': stop, 'action_counts': dict(sorted(actions.items())),
                        'failed_actions': dict(sorted(failures.items())), 'attempts': dict(sorted(attempts.items())),
                        'failed_checks': {k: dict(sorted(v.items())) for k, v in sorted(checks.items())},
                        'accepted_actions': accepted, 'empty_menu_actions': empty, 'final_failures': final,
                        'final_failures_same_batch': final[0]['round'] == final[-1]['round'] if final else None}
            if any(saved[k] != value for k, value in expected.items()):
                raise ValueError('Saved diagnosis mismatch')
            by_method[method].append(expected)
            checked += 1
            proposals += sum(attempts.values())
        for method, rows in by_method.items():
            aggregate = group['aggregate'][method]
            for key in ('action_counts', 'failed_actions', 'attempts'):
                merged = Counter()
                for row in rows:
                    merged.update(row[key])
                if aggregate[key] != dict(sorted(merged.items())):
                    raise ValueError('Aggregate mismatch')
            if (aggregate['runs'] != len(rows)
                    or aggregate['same_batch_stops'] != sum(r['final_failures_same_batch'] is True for r in rows)
                    or aggregate['different_batch_stops'] != sum(r['final_failures_same_batch'] is False for r in rows)):
                raise ValueError('Stop aggregate mismatch')
    if groups:
        raise ValueError('Missing group')
    print(json.dumps({'checked_runs': checked, 'checked_proposals': proposals}, sort_keys=True))


if __name__ == '__main__':
    main()
