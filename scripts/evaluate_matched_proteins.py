#!/usr/bin/env python3
"""Evaluate terminal matched comparison directories without overwriting outputs."""
import argparse
import json
from pathlib import Path

from app.analysis.multiprotein_evaluation import digest, evaluate_group, terminal_statuses
from app.datasets.registry import dataset_source


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path, help='New JSON report path')
    parser.add_argument('roots', type=Path, nargs='+', help='All configured protein comparison directories')
    parser.add_argument('--specification', required=True, type=Path)
    parser.add_argument('--allow-partial-development', action='store_true', help='Allow a partial, explicitly labeled development report')
    args = parser.parse_args()
    groups = []
    for root in args.roots:
        manifest = json.loads((root / 'manifest.json').read_text())
        groups.append((root, manifest, terminal_statuses(root, manifest)))
    datasets = {manifest['dataset'] for _, manifest, _ in groups}
    if len(datasets) != len(groups):
        raise ValueError('Duplicate protein group')
    expected = {'ired', 'hydro-P06241', 'hydro-P01053', 'hydro-P0A9X9'}
    if not args.allow_partial_development and datasets != expected:
        raise ValueError('Full evaluation requires all four protein groups')
    signature = lambda m: (m['seeds'], m['methods'], m['targeted_disagreement'], m['direct_diversity'], m['specification_sha256'])
    if any(signature(m) != signature(groups[0][1]) for _, m, _ in groups[1:]):
        raise ValueError('Protein group comparison settings differ')
    spec_bytes = args.specification.read_bytes()
    specification = json.loads(spec_bytes)
    if any(m['specification_sha256'] != digest(spec_bytes) for _, m, _ in groups):
        raise ValueError('Reward specification fingerprint mismatch')
    reports = []
    for root, manifest, statuses in groups:
        data, reference, loader = dataset_source(manifest['dataset'])
        _, scores, _, data_hash, reference_hash = loader(data, reference, 4)
        report = evaluate_group(root, manifest, statuses, scores, data_hash, reference_hash, specification)
        report['manifest_sha256'] = digest((root / 'manifest.json').read_bytes())
        reports.append(report)
    with args.output.open('x', encoding='utf-8') as file:
        json.dump({'scope': 'development' if args.allow_partial_development else 'four_protein',
                   'groups': reports}, file, indent=2, allow_nan=False)
        file.write('\n')


if __name__ == '__main__':
    main()
