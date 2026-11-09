#!/usr/bin/env python3
"""Fetch and validate the three planned FLIP2 benchmark splits."""
import csv
import gzip
import hashlib
import io
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1] / 'data' / 'raw' / 'flip2'
BASE = 'https://flip.protein.properties/assets/splits/'
FILES = {
    'amylase/close_to_far.csv.gz': ('e5e5f2475c01434573f26497591bc27b499d73e9e3731ed5437d2dacfdcaef9c', 3706),
    'ired/two_to_many.csv.gz': ('aa45a2f85fb1af87b6b0e86397b3f8f292a061dc574be2536673b5bd490b0e74', 8586),
    'hydro/low_to_high.csv.gz': ('4d6c778a68e0dc975f7c01967b44e0a08962bd55f89a86e142642f66816494cb', 24935),
}

def validate(data, expected_hash, expected_rows):
    if hashlib.sha256(data).hexdigest() != expected_hash:
        raise ValueError('SHA-256 mismatch; source may have changed')
    with gzip.open(io.BytesIO(data), 'rt', newline='') as handle:
        reader = csv.DictReader(handle)
        if not {'sequence', 'target', 'set', 'validation'}.issubset(reader.fieldnames or []):
            raise ValueError('Missing expected columns')
        count = sum(1 for _ in reader)
    if count != expected_rows:
        raise ValueError(f'Expected {expected_rows} rows, found {count}')
    return count

def main():
    for name, (digest, rows) in FILES.items():
        path = ROOT / name
        if path.exists():
            data = path.read_bytes()
        else:
            with urlopen(BASE + name, timeout=60) as response:
                data = response.read()
        count = validate(data, digest, rows)
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        print(f'{name}: validated {count:,} rows')

if __name__ == '__main__':
    main()
