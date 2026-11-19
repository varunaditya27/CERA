#!/usr/bin/env python3
"""Compare repair without early stopping with fixed reward and normal repair on the same starts."""
import argparse
import json
from collections import Counter
from pathlib import Path

from app.analysis.multiprotein_evaluation import verified_record
from app.datasets.registry import dataset_source
from app.experiments.evaluation import evaluate

TIE = 1e-12
SAME = ('dataset', 'initial_pool', 'seeds', 'specification_sha256', 'data_sha256', 'reference_sha256',
        'representation_cache_sha256', 'targeted_disagreement', 'direct_diversity')


def classify(value, reference):
    return 'tied' if abs(value - reference) <= TIE else 'higher' if value > reference else 'lower'


def run_summary(root, seed, method, scores, train, data_hash, reference_hash):
    path = Path(root) / f'seed_{seed:02d}' / method
    status = json.loads((path / 'status.json').read_text())
    if status['status'] != 'completed':
        raise ValueError(f'{path} did not complete')
    events = [json.loads(line) for line in verified_record(path / 'run.jsonl.gz', status).splitlines()]
    result = evaluate(events, scores, train, data_hash, reference_hash)
    curve = [(row['new_measurements'], row['best_observed']) for row in result['curve']]
    return {'curve': curve, 'best': curve[-1][1], 'measurements': curve[-1][0], 'stop_reason': result['stop_reason']}


def compare_group(old_root, new_root, scores, train, data_hash, reference_hash):
    old = json.loads((Path(old_root) / 'manifest.json').read_text())
    new = json.loads((Path(new_root) / 'manifest.json').read_text())
    if any(old[key] != new[key] for key in SAME) or new['methods'] != ['repair', 'repair_continue']:
        raise ValueError('The new study is not matched to the original study')
    rows, versus = [], {'fixed': Counter(), 'repair': Counter()}
    repeat_differs = 0
    for seed in old['seeds']:
        get = lambda root, method: run_summary(root, seed, method, scores, train, data_hash, reference_hash)
        fixed, repair, repeat, keep = get(old_root, 'fixed'), get(old_root, 'repair'), get(new_root, 'repair'), get(new_root, 'repair_continue')
        repeat_differs += repeat['curve'] != repair['curve'] or repeat['stop_reason'] != repair['stop_reason']
        versus['fixed'][classify(keep['best'], fixed['best'])] += 1
        versus['repair'][classify(keep['best'], repair['best'])] += 1
        rows.append({'seed': seed, 'fixed_best': fixed['best'], 'repair_best': repair['best'], 'repair_measurements': repair['measurements'],
                     'continue_best': keep['best'], 'continue_measurements': keep['measurements'], 'continue_stop_reason': keep['stop_reason']})
    return {'dataset': old['dataset'], 'repeat_of_repair_differs_in': repeat_differs, 'continue_vs_fixed': dict(versus['fixed']),
            'continue_vs_repair': dict(versus['repair']), 'rows': rows}


def compare_fresh(root, scores, train, data_hash, reference_hash):
    """Compare the three arms inside one study directory that ran fixed, repair and repair_continue."""
    manifest = json.loads((Path(root) / 'manifest.json').read_text())
    if manifest['methods'] != ['fixed', 'repair', 'repair_continue']:
        raise ValueError('A fresh study must run fixed, repair and repair_continue')
    rows, versus = [], {'continue_vs_fixed': Counter(), 'repair_vs_fixed': Counter(), 'continue_vs_repair': Counter()}
    for seed in manifest['seeds']:
        get = lambda method: run_summary(root, seed, method, scores, train, data_hash, reference_hash)
        fixed, repair, keep = get('fixed'), get('repair'), get('repair_continue')
        versus['continue_vs_fixed'][classify(keep['best'], fixed['best'])] += 1
        versus['repair_vs_fixed'][classify(repair['best'], fixed['best'])] += 1
        versus['continue_vs_repair'][classify(keep['best'], repair['best'])] += 1
        rows.append({'seed': seed, 'fixed_best': fixed['best'], 'repair_best': repair['best'], 'repair_measurements': repair['measurements'],
                     'continue_best': keep['best'], 'continue_measurements': keep['measurements']})
    return {'dataset': manifest['dataset'], **{key: dict(value) for key, value in versus.items()}, 'rows': rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path, help='New JSON report path')
    parser.add_argument('--pair', nargs=2, type=Path, action='append', default=[], metavar=('ORIGINAL_ROOT', 'NEW_ROOT'))
    parser.add_argument('--fresh', type=Path, action='append', default=[], metavar='ROOT')
    args = parser.parse_args()
    if not args.pair and not args.fresh:
        parser.error('Give at least one --pair or --fresh')
    groups = []
    for root in args.fresh:
        dataset = json.loads((root / 'manifest.json').read_text())['dataset']
        data, reference, loader = dataset_source(dataset)
        _, scores, train, data_hash, reference_hash = loader(data, reference, 4)
        groups.append(compare_fresh(root, scores, set(train), data_hash, reference_hash))
    for old_root, new_root in args.pair:
        dataset = json.loads((old_root / 'manifest.json').read_text())['dataset']
        data, reference, loader = dataset_source(dataset)
        _, scores, train, data_hash, reference_hash = loader(data, reference, 4)
        groups.append(compare_group(old_root, new_root, scores, set(train), data_hash, reference_hash))
    with args.output.open('x', encoding='utf-8') as file:
        json.dump({'tie_tolerance': TIE, 'groups': groups}, file, indent=2, allow_nan=False)
        file.write('\n')


if __name__ == '__main__':
    main()
