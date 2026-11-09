#!/usr/bin/env python3
"""Audit sequences, scores and existing benchmark splits without changing data."""
import collections
import csv
import gzip
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATASETS = [
 ('amylase', 'data/raw/flip2/amylase/close_to_far.csv', 3706, True),
 ('ired', 'data/raw/flip2/ired/two_to_many.csv', 8586, True),
 ('hydro', 'data/raw/flip2/hydro/low_to_high.csv', 24935, True),
 ('gb1', 'data/raw/flip/gb1/low_vs_high.csv', 8733, True),
 ('proteingym_gfp', 'data/raw/proteingym/GFP_AEQVI_Sarkisyan_2016.csv', 51714, False),
]

def main():
    for name, path, expected, split in DATASETS:
        path = ROOT / path
        if split:
            with gzip.open(str(path) + '.gz', 'rb') as source:
                if source.read() != path.read_bytes(): raise ValueError(f'{name}: extracted bytes differ')
        with path.open(newline='') as handle:
            reader = csv.DictReader(handle)
            seq_key, score_key = ('sequence', 'target') if split else ('mutated_sequence', 'DMS_score')
            required = {seq_key, score_key} | ({'set', 'validation'} if split else {'mutant'})
            if not required.issubset(reader.fieldnames or []): raise ValueError(f'{name}: missing columns')
            lengths, sets, validation, sequences = collections.Counter(), collections.Counter(), collections.Counter(), set()
            rows = 0
            for row in reader:
                rows += 1
                seq = row[seq_key]
                if not seq or set(seq) - set('ACDEFGHIKLMNPQRSTVWY'): raise ValueError(f'{name}: invalid sequence at row {rows}')
                if seq in sequences: raise ValueError(f'{name}: duplicate sequence at row {rows}')
                sequences.add(seq)
                if not math.isfinite(float(row[score_key])): raise ValueError(f'{name}: invalid score at row {rows}')
                lengths[len(seq)] += 1
                if split:
                    if row['set'] not in ('train', 'test'): raise ValueError(f'{name}: invalid set')
                    if row['validation'] not in ('True', 'False', ''): raise ValueError(f'{name}: invalid validation flag')
                    sets[row['set']] += 1
                    validation[row['validation']] += 1
            if rows != expected: raise ValueError(f'{name}: expected {expected} rows, got {rows}')
            if split and min(sets['train'], sets['test']) < 100: raise ValueError(f'{name}: split too small')
            print(f'{name}: {rows:,} rows; sequence lengths {dict(lengths)}; sets {dict(sets)}; validation {dict(validation)}')

if __name__ == '__main__': main()
