#!/usr/bin/env python3
"""Count observed near-side and far-side selections in the saved Amylase comparison."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path

from app.datasets.amylase import DATA, REFERENCE, ROOT, load_amylase

STUDY = ROOT / 'output/amylase/repair/amylase_targeted_disagreement_31_35'
METHODS = ('fixed', 'targeted')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def observed_path(seed, method, record, scores, near, data_hash, reference_hash):
    blob = (STUDY / f'seed_{seed}' / method / 'run.jsonl.gz').read_bytes()
    raw = gzip.decompress(blob)
    if (record['status'] != 'completed' or digest(blob) != record['gzip_sha256']
            or digest(raw) != record['uncompressed_sha256']):
        raise ValueError('Saved run differs from its manifest')
    start, *events = map(json.loads, raw.splitlines())
    initial = set(start['initial'])
    if (start['event'] != 'start' or start['seed'] != seed or start['max_mutations'] != 4
            or start['data_sha256'] != data_hash or start['reference_sha256'] != reference_hash
            or len(initial) != 100 or not initial <= near
            or any(value != scores[i] for i, value in start['initial'].items())):
        raise ValueError('Unexpected starting set or data sources')
    seen = set(initial)
    pending = None
    path = {0: 0}
    for event in events:
        if event['event'] == 'selection':
            ids = event['ids']
            if pending is not None or not ids or len(set(ids)) != len(ids) or set(ids) & seen:
                raise ValueError('Invalid selection history')
            pending = set(ids)
        elif event['event'] == 'reveal':
            measured = event['measurements']
            if pending != set(measured) or any(value != scores[i] for i, value in measured.items()):
                raise ValueError('Reveal disagrees with selection or source scores')
            seen.update(measured)
            path[len(seen) - len(initial)] = len(seen - near)
            pending = None
    if pending is not None:
        raise ValueError('Unfinished selection history')
    return start['initial'], path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    _, scores, train, data_hash, reference_hash = load_amylase(DATA, REFERENCE, 4)
    manifest_bytes = (STUDY / 'manifest.json').read_bytes()
    manifest = json.loads(manifest_bytes)
    if (manifest['data_sha256'], manifest['reference_sha256']) != (data_hash, reference_hash):
        raise ValueError('Study source fingerprints differ')
    expected = {f'{seed}:{method}' for seed in range(31, 36) for method in METHODS}
    if set(manifest['methods']) != expected:
        raise ValueError('Unexpected study scope')
    pairs = []
    for seed in range(31, 36):
        (fixed_start, fixed), (repair_start, repair) = [
            observed_path(seed, method, manifest['methods'][f'{seed}:{method}'], scores, set(train),
                          data_hash, reference_hash) for method in METHODS
        ]
        if fixed_start != repair_start or max(fixed) != 100 or max(repair) not in fixed:
            raise ValueError('Study pair cannot be compared at the repair stop')
        pairs.append({'seed': seed, 'repair_stop': max(repair), 'repair_far': repair[max(repair)],
                      'fixed_far_at_same_count': fixed[max(repair)], 'fixed_far_at_100': fixed[100]})
    result = {'source_manifest_sha256': digest(manifest_bytes), 'pairs': pairs}
    with args.output.open('x', encoding='utf-8') as file:
        json.dump(result, file, indent=2)
        file.write('\n')


if __name__ == '__main__':
    main()
