#!/usr/bin/env python3
"""Reconstruct historical runs and compare pre-reveal candidate rankings."""
import argparse
import csv
import gzip
import hashlib
import json
from pathlib import Path

import numpy as np

from app.features.amylase_representations import load_verified_representations
from app.analysis.disagreement_context import compare_groups
from app.analysis.warning_replay import replay_record


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source_dir', type=Path)
    parser.add_argument('prior_replay_dir', type=Path)
    parser.add_argument('output_dir', type=Path)
    args = parser.parse_args()
    with (args.source_dir / 'record_fingerprints.csv').open(newline='', encoding='utf-8') as file:
        fingerprints = {int(row['seed']): row for row in csv.DictReader(file)}
    if set(fingerprints) != set(range(2, 12)):
        raise ValueError('Unexpected historical record manifest')
    vectors = load_verified_representations()
    args.output_dir.mkdir(parents=True, exist_ok=False)
    rows, inputs = [], {}
    for seed in range(2, 12):
        source = args.source_dir / f'seed_{seed:02d}' / 'run.jsonl.gz'
        prior = args.prior_replay_dir / f'seed_{seed:02d}.jsonl'
        if digest(source) != fingerprints[seed]['gzip_sha256']:
            raise ValueError('Compressed record fingerprint mismatch')
        with gzip.open(source, 'rb') as file:
            if hashlib.sha256(file.read()).hexdigest() != fingerprints[seed]['uncompressed_sha256']:
                raise ValueError('Record content fingerprint mismatch')
        with prior.open(encoding='utf-8') as file:
            warnings = {e['round']: e for line in file if (e := json.loads(line)).get('event') == 'warning'
                        and e.get('type') == 'disagreement'}
        inputs[str(seed)] = {'source_sha256': digest(source), 'prior_replay_sha256': digest(prior)}
        run_rows = []

        def collect(round_number, models, vectors, ranked, ranges):
            result = compare_groups(seed, round_number, models, vectors, ranked, ranges)
            top = result[0]
            old = warnings[round_number]
            if top['status'] == 'unavailable':
                if old['status'] != 'unavailable':
                    raise ValueError('Prior top warning availability mismatch')
            elif old['status'] == 'unavailable' or not np.isclose(top['correlation'], old['value'], rtol=1e-10, atol=1e-12):
                raise ValueError('Prior top warning correlation mismatch')
            run_rows.extend(result)

        replay_record(source, args.output_dir / f'replay_{seed:02d}.jsonl', vectors, on_selection=collect)
        if len(run_rows) != 50 or set(warnings) != set(range(1, 11)):
            raise ValueError('Incomplete historical rounds')
        rows.extend(run_rows)
        print(f'Completed seed {seed}', flush=True)
    with (args.output_dir / 'correlations.csv').open('x', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    files = ['backend/app/analysis/disagreement_context.py', 'backend/app/analysis/warning_replay.py',
             'backend/app/predictors/predictor_group.py', 'scripts/warnings/analyze_disagreement_context.py']
    manifest = {'inputs': inputs, 'code_sha256': {path: digest(Path(path)) for path in files}}
    (args.output_dir / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
