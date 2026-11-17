#!/usr/bin/env python3
"""Compute additional descriptive metrics after matched studies terminate."""
import argparse
import json
from pathlib import Path

from app.analysis.additional_metrics import evaluate as additional_metrics
from app.analysis.multiprotein_evaluation import digest, evaluate_group, terminal_statuses, verified_record
from app.analysis.study_protocol import validate_ired_low_change, validate_low_change_pool, validate_manifests
from app.datasets.registry import dataset_source

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('roots', nargs='+', type=Path)
    parser.add_argument('--specification', type=Path, required=True)
    parser.add_argument('--ired-low-change', action='store_true')
    args = parser.parse_args()
    groups = []
    for root in args.roots:
        manifest = json.loads((root / 'manifest.json').read_text())
        groups.append((root, manifest, terminal_statuses(root, manifest)))
    manifests = [manifest for _, manifest, _ in groups]
    if args.ired_low_change:
        validate_ired_low_change(manifests)
    else:
        validate_manifests(manifests)
    spec_bytes = args.specification.read_bytes()
    if any(manifest['specification_sha256'] != digest(spec_bytes) for manifest in manifests):
        raise ValueError('Reward specification fingerprint mismatch')
    specification = json.loads(spec_bytes)
    reports = []
    for root, manifest, statuses in groups:
        data, reference_path, loader = dataset_source(manifest['dataset'])
        sequences, scores, train, data_hash, reference_hash = loader(data, reference_path, 4)
        reference = ''.join(reference_path.read_text(encoding='utf-8').splitlines()[1:])
        if args.ired_low_change:
            validate_low_change_pool(sequences, train, reference)
        verified = evaluate_group(root, manifest, statuses, scores, data_hash, reference_hash, specification,
                                  train, sequences, reference)
        rows = []
        for row in verified['summaries']:
            seed, method = row['seed'], row['method']
            if row['status'] != 'completed':
                rows.append({'seed': seed, 'method': method, 'status': row['status']})
                continue
            path = root / f'seed_{seed:02d}' / method / 'run.jsonl.gz'
            raw = verified_record(path, statuses[(seed, method)])
            events = [json.loads(line) for line in raw.splitlines()]
            metrics = additional_metrics(events, sequences, scores)
            if metrics['new_measurements'] != row['new_measurements']:
                raise ValueError('Measurement counts differ')
            rows.append({'seed': seed, 'method': method, 'status': 'completed', **metrics})
        reports.append({'dataset': manifest['dataset'], 'manifest_sha256': digest((root / 'manifest.json').read_bytes()),
                        'runs': rows})
    output = {'scope': 'ired_low_change_exploratory' if args.ired_low_change else 'four_protein_exploratory',
              'evaluator_sha256': {str(path.relative_to(ROOT)): digest(path.read_bytes()) for path in
                                   (Path(__file__).resolve(), ROOT / 'backend/app/analysis/additional_metrics.py')},
              'groups': reports}
    with args.output.open('x', encoding='utf-8') as file:
        json.dump(output, file, indent=2, allow_nan=False)
        file.write('\n')


if __name__ == '__main__':
    main()
