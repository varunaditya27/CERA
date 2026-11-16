#!/usr/bin/env python3
"""Run an exploratory amylase pilot with a validated reward specification."""
import argparse
import hashlib
import json
import os
from pathlib import Path

from app.experiments.prediction_pilot import run_pilot


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output_dir', help='New directory for run record and coverage table')
    parser.add_argument('specification', type=Path, help='JSON reward specification')
    parser.add_argument('--seed', type=int, default=1)
    parser.add_argument('--dataset', choices=('amylase', 'ired'), default='amylase')
    parser.add_argument('--repair', action='store_true', help='Enable the experimental rule-based repair loop')
    parser.add_argument('--gemini-repair', action='store_true', help='Use Gemini to prioritize repair options')
    args = parser.parse_args()
    content = args.specification.read_bytes()
    spec = json.loads(content)
    origin = {'input_sha256': hashlib.sha256(content).hexdigest(), 'source': 'specification_file'}
    if isinstance(spec, dict) and set(spec) == {'source', 'attempts', 'specification', 'model'}:
        if spec['source'] not in ('gemini', 'fallback'):
            raise ValueError('Invalid compiled specification source')
        origin.update(source=spec['source'], model=spec['model'])
        spec = spec['specification']
    advisor = model = None
    if args.gemini_repair:
        from dotenv import dotenv_values
        from app.llm.gemini_client import request_repair
        from app.llm.repair_advisor import advise_repair
        settings = dotenv_values(Path(__file__).resolve().parents[1] / 'backend' / '.env')
        key = os.environ.get('GEMINI_API_KEY') or settings.get('GEMINI_API_KEY')
        model = os.environ.get('GEMINI_MODEL') or settings.get('GEMINI_MODEL')
        advisor = lambda kind, menu: advise_repair(lambda warning, options: request_repair(key, model, warning, options),
                                                   kind, menu)
    print(json.dumps(run_pilot(args.output_dir, seed=args.seed, reward_spec=spec, reward_origin=origin,
                               repair=args.repair or args.gemini_repair, repair_advisor=advisor, repair_model=model,
                               dataset=args.dataset)))


if __name__ == '__main__':
    main()
