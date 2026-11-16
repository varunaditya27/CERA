#!/usr/bin/env python3
"""Run a matched exploratory amylase comparison and evaluate completed records."""
import argparse
import copy
import csv
import gzip
import hashlib
import json
from pathlib import Path

from app.datasets.amylase import DATA, REFERENCE, load_amylase
from app.experiments.evaluation import evaluate
from app.experiments.prediction_pilot import run_pilot
from app.experiments.random_baseline import run_random
from app.rewards.reward_spec import validate_spec


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('--seed', type=int, default=13)
    args = parser.parse_args()
    spec_path = Path('research/reward_spec_example.json')
    spec = json.loads(spec_path.read_text(encoding='utf-8'))
    validate_spec(spec)
    greedy = copy.deepcopy(spec)
    for term in greedy['terms'].values():
        term['weight'] = 0.0
    args.output.mkdir(parents=True, exist_ok=False)
    methods = ('random', 'greedy', 'fixed', 'repair')
    status = {}
    for method in methods:
        try:
            if method == 'random':
                run_random(args.output / method, args.seed)
            else:
                run_pilot(args.output / method, seed=args.seed, role_seed=2000 + args.seed,
                          member_seed=3000 + args.seed, reward_spec=greedy if method == 'greedy' else spec,
                          reward_origin={'source': 'matched_development_comparison'}, repair=method == 'repair')
            status[method] = {'status': 'completed'}
        except Exception as error:
            status[method] = {'status': 'failed', 'error_type': type(error).__name__, 'error': str(error)}
        print(json.dumps({'method': method, **status[method]}), flush=True)

    sequences, scores, train, data_hash, reference_hash = load_amylase(DATA, REFERENCE, 4)
    curves, summaries, initial = [], [], None
    for method in methods:
        if status[method]['status'] != 'completed':
            continue
        record = args.output / method / 'run.jsonl'
        raw = record.read_bytes()
        events = [json.loads(line) for line in raw.splitlines()]
        if initial is None:
            initial = events[0]['initial']
        elif initial != events[0]['initial']:
            raise ValueError('Methods have different initial observations')
        result = evaluate(events, scores, set(train), data_hash, reference_hash)
        for row in result['curve']:
            curves.append({'method': method, **row})
        summaries.append({'method': method, **result['curve'][-1], 'stop_reason': result['stop_reason'],
                          'pool_optimum': result['pool_optimum'], 'top_threshold': result['top_threshold'],
                          'covered': result['covered'], 'range_count': result['range_count'],
                          'mean_range_width': result['mean_range_width']})
        compressed_path = record.with_suffix('.jsonl.gz')
        with compressed_path.open('xb') as file:
            with gzip.GzipFile(filename='', mode='wb', fileobj=file, mtime=0) as compressed:
                compressed.write(raw)
        compressed = compressed_path.read_bytes()
        if gzip.decompress(compressed) != raw:
            raise ValueError('Record compression verification failed')
        status[method].update(uncompressed_sha256=hashlib.sha256(raw).hexdigest(),
                              gzip_sha256=hashlib.sha256(compressed).hexdigest())
        record.unlink()
    for name, rows in (('curves.csv', curves), ('summary.csv', summaries)):
        if rows:
            with (args.output / name).open('x', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)
    files = ('backend/app/experiments/evaluation.py', 'backend/app/experiments/random_baseline.py',
             'scripts/compare_reward_methods.py')
    manifest = {'seed': args.seed, 'dataset_sha256': data_hash, 'reference_sha256': reference_hash,
                'eligible_count': len(sequences), 'specification_sha256': hashlib.sha256(spec_path.read_bytes()).hexdigest(),
                'code_sha256': {file: hashlib.sha256(Path(file).read_bytes()).hexdigest() for file in files},
                'methods': status}
    (args.output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    if any(value['status'] != 'completed' for value in status.values()):
        raise SystemExit('One or more methods failed; see manifest and partial records')


if __name__ == '__main__':
    main()
