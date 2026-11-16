#!/usr/bin/env python3
"""Run an exploratory amylase pilot with a validated reward specification."""
import argparse
import json
from pathlib import Path

from app.prediction_pilot import run_pilot


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output_dir', help='New directory for run record and coverage table')
    parser.add_argument('specification', type=Path, help='JSON reward specification')
    parser.add_argument('--seed', type=int, default=1)
    args = parser.parse_args()
    spec = json.loads(args.specification.read_text(encoding='utf-8'))
    print(json.dumps(run_pilot(args.output_dir, seed=args.seed, reward_spec=spec)))


if __name__ == '__main__':
    main()
