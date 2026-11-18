#!/usr/bin/env python3
"""Describe recorded repair rejections and stopping chronology in the Hydro study."""
import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

from app.analysis.multiprotein_evaluation import terminal_statuses, verified_record
from app.analysis.study_protocol import validate_hydro_low_fitness


def analyze_actions(events):
    settings = next(e['settings'] for e in events if e['event'] == 'method')
    limit = settings['reward_spec']['abstain_after_failed_repairs']
    if limit != 2 or settings['repair'] is not True:
        raise ValueError('Unexpected repair settings')
    count, recent, last_round, stop = 0, [], 0, None
    action_counts, failures, attempts, checks = Counter(), Counter(), Counter(), defaultdict(Counter)
    accepted, empty = 0, 0
    for event in events:
        if event['event'] == 'reveal':
            stop = event['stop_reason']
        elif event['event'] == 'stop':
            stop = event['stop_reason']
        elif event['event'] == 'method' and 'repair_actions' in event['settings']:
            state = event['settings']
            round_number = state['round']
            if not isinstance(round_number, int) or round_number <= last_round:
                raise ValueError('Invalid repair round')
            last_round = round_number
            for action in state['repair_actions']:
                warning, status = action['warning'], action['status']
                if warning not in ('support_shift', 'coverage', 'disagreement', 'diversity'):
                    raise ValueError('Unknown warning')
                action_counts[f'{warning}:{status}'] += 1
                if status in ('no_replayed_targets', 'recheck_not_triggered'):
                    if action.get('attempts'):
                        raise ValueError('No-op action contains attempts')
                    continue
                if status not in ('accepted', 'retained'):
                    raise ValueError('Unknown action status')
                options = action['attempts']
                if not options:
                    empty += 1
                for item in options:
                    verification = item['verification']
                    values = verification['checks']
                    if (not values or any(value is not True and value is not False and value is not None
                                          for value in values.values())
                            or verification['accepted'] != all(value is True for value in values.values())):
                        raise ValueError('Inconsistent verification')
                    attempts[warning] += 1
                    for name, value in values.items():
                        if value is False:
                            checks[warning][f'{name}:false'] += 1
                        elif value is None:
                            checks[warning][f'{name}:unavailable'] += 1
                if status == 'accepted':
                    if not options or not options[-1]['verification']['accepted'] or any(
                            item['verification']['accepted'] for item in options[:-1]):
                        raise ValueError('Invalid accepted attempts')
                    count, recent = 0, []
                    accepted += 1
                else:
                    if any(item['verification']['accepted'] for item in options):
                        raise ValueError('Retained action contains accepted proposal')
                    count += 1
                    failures[warning] += 1
                    recent.append({'round': round_number, 'warning': warning, 'attempts': len(options)})
                if action['consecutive_failures'] != count:
                    raise ValueError('Failure counter mismatch')
            if state['consecutive_failures'] != count:
                raise ValueError('Batch failure counter mismatch')
    if stop not in ('failed_repairs', 'budget_exhausted', 'no_candidates'):
        raise ValueError('Missing or unexpected stop')
    if (stop == 'failed_repairs') != (count >= limit):
        raise ValueError('Stop does not match failure counter')
    final = recent[-limit:] if stop == 'failed_repairs' else []
    return {'stop_reason': stop, 'action_counts': dict(sorted(action_counts.items())),
            'failed_actions': dict(sorted(failures.items())), 'attempts': dict(sorted(attempts.items())),
            'failed_checks': {k: dict(sorted(v.items())) for k, v in sorted(checks.items())},
            'accepted_actions': accepted, 'empty_menu_actions': empty, 'final_failures': final,
            'final_failures_same_batch': (final[0]['round'] == final[-1]['round']) if final else None}


def aggregate(runs):
    result = {}
    for method in ('repair', 'gemini_repair'):
        selected = [r for r in runs if r['method'] == method]
        action_counts, failures, attempts, checks = Counter(), Counter(), Counter(), defaultdict(Counter)
        for run in selected:
            action_counts.update(run['action_counts'])
            failures.update(run['failed_actions'])
            attempts.update(run['attempts'])
            for warning, values in run['failed_checks'].items():
                checks[warning].update(values)
        result[method] = {'runs': len(selected),
                          'stop_reasons': dict(sorted(Counter(r['stop_reason'] for r in selected).items())),
                          'same_batch_stops': sum(r['final_failures_same_batch'] is True for r in selected),
                          'different_batch_stops': sum(r['final_failures_same_batch'] is False for r in selected),
                          'accepted_actions': sum(r['accepted_actions'] for r in selected),
                          'empty_menu_actions': sum(r['empty_menu_actions'] for r in selected),
                          'action_counts': dict(sorted(action_counts.items())),
                          'failed_actions': dict(sorted(failures.items())),
                          'attempts': dict(sorted(attempts.items())),
                          'failed_checks': {k: dict(sorted(v.items())) for k, v in sorted(checks.items())}}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('roots', nargs=3, type=Path)
    args = parser.parse_args()
    raw_report = args.report.read_bytes()
    report = json.loads(raw_report)
    if report['scope'] != 'hydro_low_fitness':
        raise ValueError('Wrong report scope')
    groups = {g['dataset']: g for g in report['groups']}
    manifests = [json.loads((root / 'manifest.json').read_text()) for root in args.roots]
    validate_hydro_low_fitness(manifests)
    result = {'report_sha256': hashlib.sha256(raw_report).hexdigest(), 'groups': []}
    for root, manifest in zip(args.roots, manifests):
        group = groups.pop(manifest['dataset'])
        if group['manifest_sha256'] != hashlib.sha256((root / 'manifest.json').read_bytes()).hexdigest():
            raise ValueError('Manifest fingerprint mismatch')
        statuses = terminal_statuses(root, manifest)
        summaries = {(r['seed'], r['method']): r for r in group['summaries']}
        runs = []
        for seed in manifest['seeds']:
            for method in ('repair', 'gemini_repair'):
                status = statuses[seed, method]
                if status['status'] != 'completed':
                    raise ValueError('Incomplete run')
                raw = verified_record(root / f'seed_{seed:02d}' / method / 'run.jsonl.gz', status)
                events = [json.loads(line) for line in raw.splitlines()]
                item = analyze_actions(events)
                expected = summaries[seed, method]
                if (item['stop_reason'] != expected['stop_reason']
                        or sum(item['attempts'].values()) != len(expected['repair_costs'])
                        or item['accepted_actions'] != expected['repairs_accepted']):
                    raise ValueError('Report and repair record mismatch')
                runs.append({'seed': seed, 'method': method, 'record_sha256': status['uncompressed_sha256'], **item})
        result['groups'].append({'dataset': manifest['dataset'], 'runs': runs, 'aggregate': aggregate(runs)})
    if groups:
        raise ValueError('Unexpected report groups')
    result['script_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    with args.output.open('x', encoding='utf-8') as file:
        json.dump(result, file, indent=2, allow_nan=False)
        file.write('\n')


if __name__ == '__main__':
    main()
