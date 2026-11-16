#!/usr/bin/env python3
"""Run an exploratory amylase pilot with a validated reward specification."""
import argparse
import hashlib
import json
from pathlib import Path

from app.prediction_pilot import run_pilot


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output_dir', help='New directory for run record and coverage table')
    parser.add_argument('specification', type=Path, help='JSON reward specification')
    parser.add_argument('--seed', type=int, default=1)
    parser.add_argument('--repair', action='store_true', help='Enable the experimental rule-based repair loop')
    args = parser.parse_args()
    content = args.specification.read_bytes()
    spec = json.loads(content)
    origin = {'input_sha256': hashlib.sha256(content).hexdigest(), 'source': 'specification_file'}
    if isinstance(spec, dict) and set(spec) == {'source', 'attempts', 'specification', 'model'}:
        if spec['source'] not in ('gemini', 'fallback'):
            raise ValueError('Invalid compiled specification source')
        origin.update(source=spec['source'], model=spec['model'])
        spec = spec['specification']
    print(json.dumps(run_pilot(args.output_dir, seed=args.seed, reward_spec=spec,
                               reward_origin=origin, repair=args.repair)))


if __name__ == '__main__':
    main()
