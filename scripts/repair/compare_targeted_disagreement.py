#!/usr/bin/env python3
"""Run the predeclared matched targeted-disagreement development comparison."""
import csv
import gzip
import hashlib
import json
from pathlib import Path
import argparse

from app.datasets.amylase import DATA, REFERENCE, load_amylase
from app.experiments.evaluation import evaluate
from app.experiments.prediction_pilot import run_pilot


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    spec_path = Path('configs/reward_spec_example.json')
    specification = json.loads(spec_path.read_text())
    args.output.mkdir(parents=True, exist_ok=False)
    status = {}
    for seed in range(31, 36):
        for method in ('fixed', 'targeted'):
            path = args.output / f'seed_{seed:02d}' / method
            try:
                run_pilot(path, seed=seed, role_seed=2000 + seed, member_seed=3000 + seed,
                          reward_spec=specification, reward_origin={'source': 'targeted_disagreement_development'},
                          repair=method == 'targeted', targeted_disagreement=method == 'targeted')
                status[f'{seed}:{method}'] = {'status': 'completed'}
            except Exception as error:
                status[f'{seed}:{method}'] = {'status': 'failed', 'error_type': type(error).__name__}
            print(json.dumps({'seed': seed, 'method': method, **status[f'{seed}:{method}']}), flush=True)
    _, scores, train, data_hash, reference_hash = load_amylase(DATA, REFERENCE, 4)
    summaries = []
    for seed in range(31, 36):
        initial = None
        for method in ('fixed', 'targeted'):
            state = status[f'{seed}:{method}']
            if state['status'] != 'completed':
                summaries.append({'seed': seed, 'method': method, 'status': state['status']})
                continue
            path = args.output / f'seed_{seed:02d}' / method
            record = path / 'run.jsonl'
            raw = record.read_bytes()
            events = [json.loads(line) for line in raw.splitlines()]
            if initial is None:
                initial = events[0]['initial']
            elif initial != events[0]['initial']:
                raise ValueError('Matched initial observations differ')
            result = evaluate(events, scores, set(train), data_hash, reference_hash)
            summaries.append({'seed': seed, 'method': method, 'status': 'completed', **result['curve'][-1],
                              'stop_reason': result['stop_reason'], 'covered': result['covered'],
                              'range_count': result['range_count'], 'mean_range_width': result['mean_range_width']})
            with (path / 'run.jsonl.gz').open('xb') as file:
                with gzip.GzipFile(filename='', mode='wb', fileobj=file, mtime=0) as compressed:
                    compressed.write(raw)
            blob = (path / 'run.jsonl.gz').read_bytes()
            if gzip.decompress(blob) != raw:
                raise ValueError('Record compression mismatch')
            state.update(uncompressed_sha256=hashlib.sha256(raw).hexdigest(), gzip_sha256=hashlib.sha256(blob).hexdigest())
            record.unlink()
    columns = ('seed', 'method', 'status', 'new_measurements', 'best_observed', 'pool_regret',
               'found_top_one_percent', 'stop_reason', 'covered', 'range_count', 'mean_range_width')
    with (args.output / 'summary.csv').open('x', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=columns, lineterminator='\n')
        writer.writeheader()
        writer.writerows(summaries)
    manifest = {'methods': status, 'data_sha256': data_hash, 'reference_sha256': reference_hash,
                'specification_sha256': hashlib.sha256(spec_path.read_bytes()).hexdigest(),
                'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (args.output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    if any(item['status'] != 'completed' for item in status.values()):
        raise SystemExit('Some runs failed; see manifest and partial records')


if __name__ == '__main__':
    main()
