#!/usr/bin/env python3
"""Replay the fixed ten-pair Amylase predictor comparison and report its results."""
import argparse
from collections import Counter
import gzip
import hashlib
import json
import sys
from pathlib import Path
import tempfile

from app.datasets.amylase import DATA, REFERENCE, load_amylase
from app.experiments.evaluation import evaluate
from app.features.amylase_representations import CACHE_SHA256
from app.provenance.sources import CodeChanged, require_recorded_code, source_hashes
from scripts.reporting.legacy_audit import rerun_with_recorded_code
from scripts.repair.audit_development_repairs import audit_run
from scripts.hybrid.audit_hybrid_pilot import audit_record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    parser.add_argument('specification', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('Output already exists')
    spec_bytes = args.specification.read_bytes()
    spec = json.loads(spec_bytes)
    sequences, scores, train, data_hash, ref_hash = load_amylase(DATA, REFERENCE, 4)
    results, counts = [], Counter()
    for seed in range(191, 201):
        pair = {}
        for method in ('ridge', 'mixed'):
            directory = args.directory / f'{seed}_{method}'
            record = directory / 'run.jsonl'
            compressed = directory / 'run.jsonl.gz'
            if record.exists() == compressed.exists():
                raise ValueError('Expected exactly one run record')
            raw = record.read_bytes() if record.exists() else gzip.decompress(compressed.read_bytes())
            events = [json.loads(line) for line in raw.splitlines()]
            setup = next(event['settings'] for event in events if event['event'] == 'method')
            expected_method = 'esm_hybrid_reward' if method == 'mixed' else 'esm_bootstrap_ridge_reward'
            require_recorded_code(setup['source_sha256'] == source_hashes(tuple(setup['source_sha256'])))
            if (setup['method'] != expected_method or setup['reward_spec'] != spec
                    or setup['reward_origin'] != {'source': 'specification_file', 'input_sha256': hashlib.sha256(spec_bytes).hexdigest()}
                    or setup['dataset'] != 'amylase' or setup['cache_sha256'] != CACHE_SHA256):
                raise ValueError('Method or dataset mismatch')
            evaluation = evaluate(events, scores, set(train), data_hash, ref_hash)
            row = {'status': 'completed', **evaluation['curve'][-1], 'stop_reason': evaluation['stop_reason'],
                   'covered': evaluation['covered'], 'range_count': evaluation['range_count'],
                   'mean_range_width': evaluation['mean_range_width']}
            row['found_top_one_percent'] = str(row['found_top_one_percent'])
            audit_run(events, seed, 'fixed', sequences, scores, train,
                      {'data_sha256': data_hash, 'reference_sha256': ref_hash}, row, counts,
                      hybrid_device='cuda' if method == 'mixed' else None, role_seed=3, member_seed=4)
            if method == 'mixed':
                if record.exists():
                    audit_record(record, args.specification, seed, 'cuda', False)
                else:
                    with tempfile.TemporaryDirectory() as temporary:
                        unpacked = Path(temporary) / 'run.jsonl'
                        unpacked.write_bytes(raw)
                        audit_record(unpacked, args.specification, seed, 'cuda', False)
            if row['new_measurements'] != 100 or row['range_count'] != 100 or row['stop_reason'] != 'budget_exhausted':
                raise ValueError('Incomplete equal-budget comparison')
            log = json.loads((args.directory / f'{seed}_{method}.log').read_text())
            pair[method] = {'record_sha256': hashlib.sha256(raw).hexdigest(),
                            'best_observed': row['best_observed'], 'covered': row['covered'],
                            'range_count': row['range_count'], 'mean_range_width': row['mean_range_width'],
                            'elapsed_seconds': log['seconds']}
            pair[method]['initial_sha256'] = hashlib.sha256(json.dumps(events[0]['initial'], sort_keys=True).encode()).hexdigest()
            pair[method]['reserved_ids'] = setup['reserved_ids']
        if (pair['ridge']['initial_sha256'] != pair['mixed']['initial_sha256']
                or pair['ridge']['reserved_ids'] != pair['mixed']['reserved_ids']):
            raise ValueError('Matched starts or reserved identifiers differ')
        results.append({'seed': seed, **pair})
    differences = [p['mixed']['best_observed'] - p['ridge']['best_observed'] for p in results]
    result = {'seeds': list(range(191, 201)), 'runs': results, 'audit_counts': dict(counts),
              'mixed_higher': sum(d > 0 for d in differences), 'ties': sum(d == 0 for d in differences),
              'ridge_higher': sum(d < 0 for d in differences)}
    with args.output.open('x', encoding='utf-8') as file:
        json.dump(result, file, indent=2, allow_nan=False)
        file.write('\n')
    print(json.dumps({key: value for key, value in result.items() if key != 'runs'}, sort_keys=True))


if __name__ == '__main__':
    try:
        main()
    except CodeChanged:
        sys.exit(rerun_with_recorded_code('audit_mixed_search_comparison', 'pre-restructure'))
