#!/usr/bin/env python3
"""Run a matched Amylase development comparison of repair safeguards."""
import argparse
import csv
import gzip
import json
import platform
import time
from importlib.metadata import version
from pathlib import Path

from app.datasets.amylase import DATA, REFERENCE, load_amylase
from app.analysis.study_protocol import SPECIFICATION_SHA256
from app.experiments.evaluation import evaluate
from app.experiments.prediction_pilot import run_pilot
from app.features.amylase_representations import CACHE
from app.rewards.reward_spec import validate_spec
from repeated_matched import ROOT, digest, write_json

SEEDS = tuple(range(71, 76))
EVIDENCE_SEEDS = tuple(range(81, 86))
TERM_SEEDS = tuple(range(91, 96))
UNIVERSAL_SEEDS = tuple(range(101, 106))
RETENTION_SEEDS = tuple(range(111, 116))
ROLLBACK_SEEDS = tuple(range(161, 166))
CALIBRATION_SEEDS = tuple(range(171, 176))
METHODS = ('normal', 'continue')
REMOVED_TERMS = {'no_distance': 'distance_penalty', 'no_uncertainty': 'uncertainty_penalty',
                 'no_diversity': 'diversity_bonus'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('--resume', action='store_true')
    parser.add_argument('--comparison', choices=('stopping', 'evidence', 'repair-terms', 'universal', 'retention', 'later-rollback', 'reactive-calibration'), default='stopping')
    args = parser.parse_args()
    if args.comparison == 'stopping':
        seeds, methods = SEEDS, METHODS
    elif args.comparison == 'evidence':
        seeds, methods = EVIDENCE_SEEDS, ('normal', 'bypass')
    elif args.comparison == 'repair-terms':
        seeds, methods = TERM_SEEDS, ('normal', *REMOVED_TERMS)
    elif args.comparison == 'universal':
        seeds, methods = UNIVERSAL_SEEDS, ('normal', 'universal')
    elif args.comparison == 'retention':
        seeds, methods = RETENTION_SEEDS, ('normal', 'no_retention')
    elif args.comparison == 'later-rollback':
        seeds, methods = ROLLBACK_SEEDS, ('normal', 'rollback')
    else:
        seeds, methods = CALIBRATION_SEEDS, ('normal', 'reactive')
    if (args.output / 'summary.csv').exists():
        raise ValueError('Completed comparison summary already exists')
    spec_bytes = (ROOT / 'research/reward_spec_example.json').read_bytes()
    if digest(spec_bytes) != SPECIFICATION_SHA256:
        raise ValueError('Reward specification does not match the development protocol')
    spec = json.loads(spec_bytes)
    validate_spec(spec)
    paths = sorted((ROOT / 'backend/app').rglob('*.py')) + [Path(__file__).resolve(), ROOT / 'scripts/repeated_matched.py']
    manifest = {'seeds': list(seeds), 'methods': list(methods), 'dataset': 'amylase', 'comparison': args.comparison,
                'data_sha256': digest(DATA.read_bytes()), 'reference_sha256': digest(REFERENCE.read_bytes()),
                'cache_sha256': digest(CACHE.read_bytes()), 'specification_sha256': digest(spec_bytes),
                'python': platform.python_version(),
                'versions': {name: version(name) for name in ('numpy', 'scipy', 'scikit-learn')},
                'code_sha256': {str(path.relative_to(ROOT)): digest(path.read_bytes()) for path in paths}}
    if args.resume:
        if json.loads((args.output / 'manifest.json').read_text()) != manifest:
            raise ValueError('Cannot resume with changed inputs or code')
    else:
        args.output.mkdir(parents=True, exist_ok=False)
        write_json(args.output / 'manifest.json', manifest)
    for seed in seeds:
        for method in methods:
            path = args.output / f'seed_{seed:02d}' / method
            status_path = path / 'status.json'
            if status_path.exists():
                status = json.loads(status_path.read_text())
                if status['status'] == 'completed':
                    blob = (path / 'run.jsonl.gz').read_bytes()
                    if digest(blob) != status['gzip_sha256'] or digest(gzip.decompress(blob)) != status['uncompressed_sha256']:
                        raise ValueError('Completed record fingerprint mismatch')
                continue
            if path.exists():
                write_json(status_path, {'status': 'interrupted'})
                continue
            started = time.perf_counter()
            try:
                run_pilot(path, seed=seed, role_seed=2000 + seed, member_seed=3000 + seed,
                          reward_spec=spec, reward_origin={'source': f'{args.comparison}_development'},
                          repair=args.comparison != 'reactive-calibration',
                          targeted_disagreement=args.comparison != 'reactive-calibration',
                          direct_diversity=args.comparison != 'reactive-calibration',
                          stop_on_failed_repairs=method != 'continue', bypass_evidence_gate=method == 'bypass',
                          disabled_repair_terms=(REMOVED_TERMS[method],) if method in REMOVED_TERMS else (),
                          universal_penalty=method == 'universal', apply_last_rejected=method == 'no_retention',
                          rollback_monitor=method == 'rollback', reactive_calibration=method == 'reactive')
                raw = (path / 'run.jsonl').read_bytes()
                blob = gzip.compress(raw, mtime=0)
                with (path / 'run.jsonl.gz').open('xb') as file:
                    file.write(blob)
                if gzip.decompress(blob) != raw:
                    raise ValueError('Compressed record mismatch')
                status = {'status': 'completed', 'elapsed_seconds': time.perf_counter() - started,
                          'gzip_sha256': digest(blob), 'uncompressed_sha256': digest(raw)}
                write_json(status_path, status)
                (path / 'run.jsonl').unlink()
            except Exception as error:
                path.mkdir(parents=True, exist_ok=True)
                status = {'status': 'failed', 'error_type': type(error).__name__,
                          'elapsed_seconds': time.perf_counter() - started}
                write_json(status_path, status)
            print(json.dumps({'seed': seed, 'method': method, 'status': status['status']}), flush=True)
    for seed in seeds:
        for method in methods:
            path = args.output / f'seed_{seed:02d}' / method / 'status.json'
            if not path.is_file() or json.loads(path.read_text()).get('status') not in ('completed', 'failed', 'interrupted'):
                raise ValueError('Not all runs have terminal status')
    _, scores, train, data_hash, reference_hash = load_amylase(DATA, REFERENCE, 4)
    rows = []
    for seed in seeds:
        initial = None
        for method in methods:
            path = args.output / f'seed_{seed:02d}' / method
            state = json.loads((path / 'status.json').read_text())
            if state['status'] != 'completed':
                rows.append({'seed': seed, 'method': method, 'status': state['status']})
                continue
            blob = (path / 'run.jsonl.gz').read_bytes()
            if digest(blob) != state['gzip_sha256']:
                raise ValueError('Compressed record fingerprint mismatch')
            raw = gzip.decompress(blob)
            if digest(raw) != state['uncompressed_sha256']:
                raise ValueError('Record fingerprint mismatch')
            events = [json.loads(line) for line in raw.splitlines()]
            if initial is not None and initial != events[0]['initial']:
                raise ValueError('Matched starts differ')
            initial = events[0]['initial']
            result = evaluate(events, scores, set(train), data_hash, reference_hash)
            actions = [a for e in events if e['event'] == 'method' for a in e['settings'].get('repair_actions', [])]
            rows.append({'seed': seed, 'method': method, 'status': 'completed', **result['curve'][-1],
                         'stop_reason': result['stop_reason'], 'covered': result['covered'],
                         'range_count': result['range_count'], 'mean_range_width': result['mean_range_width'],
                         'repair_actions': len(actions), 'repairs_accepted': sum(a['status'] == 'accepted' for a in actions),
                         'disabled_actions': sum(a['status'] == 'repair_disabled' for a in actions),
                         'rejected_repairs_applied': sum(a['status'] == 'applied_rejected' for a in actions),
                         'calibration_updates': sum('calibration_update' in e.get('settings', {}) for e in events),
                         'accepted_without_evidence': sum(a['status'] == 'accepted' and
                             not a['attempts'][-1]['verification']['accepted'] for a in actions)})
    columns = ('seed', 'method', 'status', 'new_measurements', 'best_observed', 'pool_regret',
               'found_top_one_percent', 'stop_reason', 'covered', 'range_count', 'mean_range_width',
               'repair_actions', 'repairs_accepted', 'disabled_actions', 'rejected_repairs_applied',
               'accepted_without_evidence', 'calibration_updates')
    with (args.output / 'summary.csv').open('x', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=columns, lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
    if any(row['status'] != 'completed' for row in rows):
        raise SystemExit('Some runs failed or were interrupted; inspect their records')


if __name__ == '__main__':
    main()
