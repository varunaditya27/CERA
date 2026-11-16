#!/usr/bin/env python3
"""Run one exploratory amylase prediction-range pilot."""
import argparse
import json

from app.experiments.prediction_pilot import run_pilot


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output_dir', help='New directory for run record and coverage table')
    parser.add_argument('--seed', type=int, default=1)
    args = parser.parse_args()
    print(json.dumps(run_pilot(args.output_dir, seed=args.seed)))


if __name__ == '__main__':
    main()
