#!/usr/bin/env python3
"""Replay warning checks on the ten recorded amylase range runs."""
import argparse
import csv
import gzip
import hashlib
import json
from pathlib import Path

from app.amylase_representations import load_verified_representations
from app.warning_replay import replay_record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source_dir', type=Path)
    parser.add_argument('output_dir', type=Path, help='New directory for replay evidence')
    args = parser.parse_args()
    vectors = load_verified_representations()
    with (args.source_dir / 'record_fingerprints.csv').open(newline='', encoding='utf-8') as file:
        fingerprints = {int(row['seed']): row for row in csv.DictReader(file)}
    if set(fingerprints) != set(range(2, 12)):
        raise ValueError('Historical record manifest does not list the expected seeds')
    args.output_dir.mkdir(parents=True, exist_ok=False)
    for seed in range(2, 12):
        source = args.source_dir / f'seed_{seed:02d}' / 'run.jsonl.gz'
        expected = fingerprints[seed]
        if hashlib.sha256(source.read_bytes()).hexdigest() != expected['gzip_sha256']:
            raise ValueError('Compressed historical record fingerprint mismatch')
        with gzip.open(source, 'rb') as file:
            if hashlib.sha256(file.read()).hexdigest() != expected['uncompressed_sha256']:
                raise ValueError('Historical record content fingerprint mismatch')
        result = replay_record(source, args.output_dir / f'seed_{seed:02d}.jsonl', vectors)
        print(json.dumps({'seed': seed, 'warning_counts': result}), flush=True)


if __name__ == '__main__':
    main()
