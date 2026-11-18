#!/usr/bin/env python3
"""Summarize a completed run's coverage-warning recovery from its saved record."""
import argparse
import gzip
import json
from pathlib import Path

from app.analysis.recovery import summarize_recovery


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('record', type=Path)
    args = parser.parse_args()
    opener = gzip.open if args.record.suffix == '.gz' else open
    with opener(args.record, 'rt', encoding='utf-8') as file:
        print(json.dumps(summarize_recovery(json.loads(line) for line in file), indent=2))


if __name__ == '__main__':
    main()
