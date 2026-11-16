"""Fingerprint named application modules independent of their package location."""
import hashlib
from pathlib import Path

APP = Path(__file__).resolve().parents[1]


def source_hashes(names):
    result = {}
    for name in names:
        if Path(name).name != name:
            raise ValueError('Invalid source filename')
        matches = list(APP.rglob(name))
        if len(matches) != 1 or not matches[0].is_file():
            raise ValueError(f'Expected one application source for {name}')
        result[name] = hashlib.sha256(matches[0].read_bytes()).hexdigest()
    return result
