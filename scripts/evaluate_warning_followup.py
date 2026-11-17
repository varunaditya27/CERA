#!/usr/bin/env python3
"""Evaluate historical development warnings against later observed coverage."""
import csv
import gzip
import hashlib
import json
from pathlib import Path

from app.analysis.warning_followup import KINDS, evaluate, summarize

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'output/amylase_ranges_repeated'
REPLAY = ROOT / 'output/amylase_warning_replay_v2'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    with (SOURCE / 'record_fingerprints.csv').open(newline='', encoding='utf-8') as file:
        manifest = {int(row['seed']): row for row in csv.DictReader(file)}
    if set(manifest) != set(range(2, 12)):
        raise ValueError('Unexpected source seeds')
    records, inputs = [], {}
    for seed, expected in sorted(manifest.items()):
        compressed = (SOURCE / f'seed_{seed:02d}/run.jsonl.gz').read_bytes()
        if digest(compressed) != expected['gzip_sha256']:
            raise ValueError('Compressed source fingerprint mismatch')
        raw = gzip.decompress(compressed)
        if digest(raw) != expected['uncompressed_sha256']:
            raise ValueError('Source content fingerprint mismatch')
        replay_raw = (REPLAY / f'seed_{seed:02d}.jsonl').read_bytes()
        source = [json.loads(line) for line in raw.splitlines()]
        replay = [json.loads(line) for line in replay_raw.splitlines()]
        if (source[0]['event'] != 'start' or source[0]['seed'] != seed or
                replay[0]['event'] != 'replay_start' or replay[0]['source_sha256'] != digest(compressed) or
                replay[-1]['event'] != 'replay_end' or not source[-1].get('stop_reason')):
            raise ValueError('Invalid source or replay provenance')
        rows = evaluate(source, replay)
        if replay[-1]['rounds'] != len(rows) // len(KINDS):
            raise ValueError('Replay round count mismatch')
        records.extend({'seed': seed, **row} for row in rows)
        inputs[str(seed)] = {'source_gzip_sha256': digest(compressed), 'replay_sha256': digest(replay_raw)}
    result = {'scope': 'exploratory Amylase development; not independent validation', 'inputs': inputs,
              'evaluator_sha256': {str(path.relative_to(ROOT)): digest(path.read_bytes()) for path in
                                   (Path(__file__).resolve(), ROOT / 'backend/app/analysis/warning_followup.py')},
              'overall': {kind: summarize([row for row in records if row['warning'] == kind]) for kind in KINDS},
              'per_seed': {str(seed): {kind: summarize([row for row in records
                           if row['seed'] == seed and row['warning'] == kind]) for kind in KINDS}
                           for seed in sorted(manifest)}, 'rows': records}
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
