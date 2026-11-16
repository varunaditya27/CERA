#!/usr/bin/env python3
"""Run one exploratory amylase prediction-range pilot."""
import argparse
import json

from app.experiments.prediction_pilot import run_pilot


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output_dir', help='New directory for run record and coverage table')
    parser.add_argument('--seed', type=int, default=1)
    parser.add_argument('--role-seed', type=int, default=3)
    parser.add_argument('--member-seed', type=int, default=4)
    parser.add_argument('--dataset', choices=('amylase', 'ired', 'hydro-P06241', 'hydro-P01053', 'hydro-P0A9X9'),
                        default='amylase')
    parser.add_argument('--acquisition', choices=('ucb', 'ei'))
    parser.add_argument('--local-search', choices=('genetic', 'adalead'))
    args = parser.parse_args()
    print(json.dumps(run_pilot(args.output_dir, seed=args.seed, role_seed=args.role_seed,
                               member_seed=args.member_seed, dataset=args.dataset, acquisition=args.acquisition,
                               local_search=args.local_search)))


if __name__ == '__main__':
    main()
