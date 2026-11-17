#!/usr/bin/env python3
"""Recalculate search outcomes and coverage directly from compressed records."""
import argparse
import gzip
import hashlib
import json
import math
from pathlib import Path

from app.datasets.registry import dataset_source
from app.experiments.repeated_runs import METHODS


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report', type=Path)
    parser.add_argument('roots', nargs=3, type=Path)
    args = parser.parse_args()
    report_raw = args.report.read_bytes()
    report = json.loads(report_raw)
    if report['scope'] != 'hydro_low_fitness' or len(report['groups']) != 3:
        raise ValueError('Wrong report scope')
    groups = {g['dataset']: g for g in report['groups']}
    checked_runs = checked_measurements = 0
    for root in args.roots:
        manifest = json.loads((root / 'manifest.json').read_text())
        dataset = manifest['dataset']
        group = groups.pop(dataset)
        if group['manifest_sha256'] != digest((root / 'manifest.json').read_bytes()):
            raise ValueError('Manifest mismatch')
        data, reference, loader = dataset_source(dataset)
        sequences, scores, train, data_hash, reference_hash = loader(data, reference, 4)
        if (data_hash, reference_hash) != (manifest['data_sha256'], manifest['reference_sha256']):
            raise ValueError('Source mismatch')
        test = set(scores) - set(train)
        rows = {(r['seed'], r['method']): r for r in group['summaries']}
        if len(group['summaries']) != 90 or set(rows) != {(s, m) for s in range(141, 151) for m in METHODS}:
            raise ValueError('Run list mismatch')
        for (seed, method), row in rows.items():
            directory = root / f'seed_{seed:02d}' / method
            status = json.loads((directory / 'status.json').read_text())
            blob = (directory / 'run.jsonl.gz').read_bytes()
            raw = gzip.decompress(blob)
            if status['status'] != 'completed' or digest(blob) != status['gzip_sha256'] or digest(raw) != status['uncompressed_sha256']:
                raise ValueError('Record mismatch')
            events = [json.loads(line) for line in raw.splitlines()]
            known = dict(events[0]['initial'])
            selected, covered, width, pending = [], 0, 0.0, None
            best_curve = [(0, max(known.values()))]
            stop = None
            for event in events[1:]:
                if event['event'] == 'selection':
                    if pending is not None:
                        raise ValueError('Selection chronology mismatch')
                    pending = event
                elif event['event'] == 'reveal':
                    if pending is None or pending['ids'] != list(event['measurements']):
                        raise ValueError('Reveal chronology mismatch')
                    for identifier, score in event['measurements'].items():
                        if identifier in known or score != scores[identifier]:
                            raise ValueError('Score mismatch')
                        known[identifier] = score
                        selected.append(identifier)
                        if method != 'random':
                            interval = pending['prediction_ranges'][identifier]
                            covered += interval['lower'] <= score <= interval['upper']
                            width += interval['upper'] - interval['lower']
                    stop = event['stop_reason']
                    best_curve.append((len(selected), max(known.values())))
                    pending = None
                elif event['event'] == 'stop':
                    stop = event['stop_reason']
            n = len(selected)
            saved_curve = [(entry['new_measurements'], entry['best_observed']) for entry in group['curves']
                           if entry['seed'] == seed and entry['method'] == method]
            if saved_curve != best_curve:
                raise ValueError('Best-score curve mismatch')
            if (pending is not None or row['status'] != 'completed' or row['stop_reason'] != stop
                    or row['new_measurements'] != n or row['best_observed'] != max(known.values())
                    or row['selected_split_counts'] != {'train': sum(i not in test for i in selected),
                                                        'test': sum(i in test for i in selected)}
                    or row['covered'] != (None if method == 'random' else covered)
                    or row['range_count'] != (0 if method == 'random' else n)
                    or (method != 'random' and n and not math.isclose(row['mean_range_width'], width / n,
                                                                    rel_tol=1e-10, abs_tol=1e-10))):
                raise ValueError('Outcome mismatch')
            checked_runs += 1
            checked_measurements += n
    if groups:
        raise ValueError('Missing group')
    print(json.dumps({'report_sha256': digest(report_raw), 'checked_runs': checked_runs,
                      'checked_measurements': checked_measurements}, sort_keys=True))


if __name__ == '__main__':
    main()
