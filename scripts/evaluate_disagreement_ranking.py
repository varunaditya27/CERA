#!/usr/bin/env python3
"""Describe saved disagreement warnings and measured batch rankings."""
import csv
import gzip
import hashlib
import json
import statistics
from pathlib import Path

from app.analysis.disagreement_ranking import evaluate

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'output/amylase_ranges_repeated'
REPLAY = ROOT / 'output/amylase_warning_replay_v2'


def digest(value):
    return hashlib.sha256(value).hexdigest()


def main():
    with (SOURCE / 'record_fingerprints.csv').open(newline='', encoding='utf-8') as file:
        manifest = {int(row['seed']): row for row in csv.DictReader(file)}
    if set(manifest) != set(range(2, 12)):
        raise ValueError('Unexpected seeds')
    rows, inputs = [], {}
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
        if (source[0]['event'] != 'start' or source[0]['seed'] != seed or not source[-1].get('stop_reason')
                or replay[0]['event'] != 'replay_start' or replay[0]['source_sha256'] != digest(compressed)
                or replay[-1]['event'] != 'replay_end'):
            raise ValueError('Invalid source or replay provenance')
        result = evaluate(source, replay)
        if replay[-1]['rounds'] != len(result):
            raise ValueError('Replay round count mismatch')
        rows.extend({'seed': seed, **row} for row in result)
        inputs[str(seed)] = {'source_gzip_sha256': digest(compressed), 'replay_sha256': digest(replay_raw)}
    summary = {}
    for status in ('triggered', 'not_triggered', 'unavailable'):
        selected = [row for row in rows if row['warning'] == status]
        values = [row['spearman'] for row in selected if row['spearman'] is not None]
        summary[status] = {'batches': len(selected), 'defined': len(values),
                           'median': statistics.median(values) if values else None}
    print(json.dumps({'scope': 'exploratory Amylase development; not independent validation',
                      'inputs': inputs, 'evaluator_sha256': {str(path.relative_to(ROOT)): digest(path.read_bytes())
                      for path in (Path(__file__).resolve(), ROOT / 'backend/app/analysis/disagreement_ranking.py')},
                      'summary': summary, 'rows': rows}, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
