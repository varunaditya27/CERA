#!/usr/bin/env python3
"""Evaluate terminal matched comparison directories without overwriting outputs."""
import argparse
import json
from pathlib import Path

from app.analysis.multiprotein_evaluation import digest, evaluate_group, terminal_statuses
from app.analysis.study_protocol import validate_hydro_low_fitness, validate_ired_low_change, validate_low_change_pool, validate_manifests
from app.datasets.registry import dataset_source


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path, help='New JSON report path')
    parser.add_argument('roots', type=Path, nargs='+', help='All configured protein comparison directories')
    parser.add_argument('--specification', required=True, type=Path)
    parser.add_argument('--allow-partial-development', action='store_true', help='Allow a partial, explicitly labeled development report')
    parser.add_argument('--ired-low-change', action='store_true', help='Evaluate the separate IRED low-change study')
    parser.add_argument('--hydro-low-fitness', action='store_true', help='Use the Hydro low-fitness-start study scope')
    args = parser.parse_args()
    if sum((args.ired_low_change, args.hydro_low_fitness, args.allow_partial_development)) > 1:
        raise ValueError('Study and partial development scopes cannot be combined')
    groups = []
    for root in args.roots:
        manifest = json.loads((root / 'manifest.json').read_text())
        groups.append((root, manifest, terminal_statuses(root, manifest)))
    manifests = [manifest for _, manifest, _ in groups]
    if args.ired_low_change:
        validate_ired_low_change(manifests)
    elif args.hydro_low_fitness:
        validate_hydro_low_fitness(manifests)
    else:
        validate_manifests(manifests, args.allow_partial_development)
    spec_bytes = args.specification.read_bytes()
    specification = json.loads(spec_bytes)
    if any(m['specification_sha256'] != digest(spec_bytes) for _, m, _ in groups):
        raise ValueError('Reward specification fingerprint mismatch')
    reports = []
    for root, manifest, statuses in groups:
        data, reference, loader = dataset_source(manifest['dataset'])
        sequences, scores, train, data_hash, reference_hash = loader(data, reference, 4)
        reference_sequence = ''.join(reference.read_text(encoding='utf-8').splitlines()[1:])
        if args.ired_low_change:
            validate_low_change_pool(sequences, train, reference_sequence)
        report = evaluate_group(root, manifest, statuses, scores, data_hash, reference_hash, specification,
                                train, sequences, reference_sequence)
        report['manifest_sha256'] = digest((root / 'manifest.json').read_bytes())
        reports.append(report)
    with args.output.open('x', encoding='utf-8') as file:
        json.dump({'scope': 'ired_low_change' if args.ired_low_change else
                   'hydro_low_fitness' if args.hydro_low_fitness else
                   'development' if args.allow_partial_development else 'four_protein',
                   'groups': reports}, file, indent=2, allow_nan=False)
        file.write('\n')


if __name__ == '__main__':
    main()
