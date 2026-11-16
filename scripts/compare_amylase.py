#!/usr/bin/env python3
"""Run one exploratory matched amylase comparison."""
import argparse

from app.experiments.comparison import run_comparison


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output_dir', help='New directory for run records and summaries')
    parser.add_argument('--seed', type=int, default=1, help='Starting-set seed')
    args = parser.parse_args()
    run_comparison(args.output_dir, seed=args.seed)


if __name__ == '__main__':
    main()
