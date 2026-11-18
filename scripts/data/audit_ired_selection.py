#!/usr/bin/env python3
"""Compare the local IRED split with the laboratory's active-data table."""
import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPLIT = ROOT / 'data/raw/flip2/ired/two_to_many.csv'
ACTIVE_SHA256 = '81964bd5f366310627641ddaba573d77242803969570aa383d9f3912364adc0b'
ACTIVE_URL = ('https://github.com/Hollfelder-Lab/lrDMS-IRED/blob/6a9e87c6c788e77d67e9e7ccad1208f1f60f859c/'
              'data/srired_active_data.csv')


def compare(active, split_sequences):
    """Classify every active-table row as inside or outside the split and say why it was left out."""
    sequence = lambda row: row['aa_seq'].rstrip('*')
    inside = [row for row in active if sequence(row) in split_sequences]
    outside = [row for row in active if sequence(row) not in split_sequences]
    clean = lambda row: row['indel'] == 'False' and row['STOP'] == 'False' and row['STOP_readthrough'] == 'False'
    changes = lambda rows: sorted(float(row['Nham_aa']) for row in rows)
    return {
        'active_rows': len(active),
        'split_rows': len(split_sequences),
        'split_rows_missing_from_active': len(split_sequences - {sequence(row) for row in active}),
        'active_rows_in_split': len(inside),
        'active_rows_left_out': len(outside),
        'left_out_flags': {key: sum(row[key] == 'True' for row in outside) for key in ('indel', 'STOP', 'STOP_readthrough')},
        'flag_free_rows_in_split': sum(clean(row) for row in inside),
        'flagged_rows_in_split': sum(not clean(row) for row in inside),
        'flag_free_rows_left_out': len([row for row in outside if clean(row)]),
        'flag_free_left_out_amino_acid_changes': changes([row for row in outside if clean(row)]),
        'most_amino_acid_changes_in_split': max(changes(inside)),
        'flag_free_rows_with_changes_between_split_maximum_and_smallest_left_out': len([
            row for row in active if clean(row) and max(changes(inside)) < float(row['Nham_aa']) < min(changes([r for r in outside if clean(r)]) or [float('inf')])]),
        'amino_acid_changes_in_split': dict(sorted((int(float(k)), v) for k, v in Counter(row['Nham_aa'] for row in inside).items())),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__ + f' Download the table from {ACTIVE_URL} (raw file).')
    parser.add_argument('active_table', type=Path)
    args = parser.parse_args()
    raw = args.active_table.read_bytes()
    if hashlib.sha256(raw).hexdigest() != ACTIVE_SHA256:
        raise SystemExit('Active table does not match the pinned SHA-256')
    active = list(csv.DictReader(raw.decode().splitlines()))
    with SPLIT.open() as handle:
        split_sequences = {row['sequence'] for row in csv.DictReader(handle)}
    print(json.dumps(compare(active, split_sequences), indent=2))


if __name__ == '__main__':
    main()
