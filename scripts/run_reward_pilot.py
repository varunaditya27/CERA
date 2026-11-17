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
    parser.add_argument('--dataset', choices=('amylase', 'ired', 'hydro-P06241', 'hydro-P01053', 'hydro-P0A9X9'),
                        default='amylase')
    parser.add_argument('--repair', action='store_true', help='Enable the experimental rule-based repair loop')
    parser.add_argument('--gemini-repair', action='store_true', help='Use Gemini to prioritize repair options')
    parser.add_argument('--targeted-disagreement', action='store_true', help='Use the experimental disagreement target rule')
    parser.add_argument('--hybrid-device', choices=('cpu', 'cuda'), help='Use the experimental mixed predictor on this device')
    parser.add_argument('--reactive-calibration', action='store_true', help='Update range-setting examples after a warning in Amylase development')
    parser.add_argument('--rollback-monitor', action='store_true', help='Enable later-coverage rollback in Amylase development')
    parser.add_argument('--direct-diversity', action='store_true', help='Check whether a replay resolves the diversity warning')
    args = parser.parse_args()
    content = args.specification.read_bytes()
    spec = json.loads(content)
    origin = {'input_sha256': hashlib.sha256(content).hexdigest(), 'source': 'specification_file'}
    compiled_keys = {'source', 'attempts', 'specification', 'model'}
    if isinstance(spec, dict) and set(spec) in (compiled_keys, compiled_keys | {'input_goal'}):
        if spec['source'] not in ('gemini', 'fallback'):
            raise ValueError('Invalid compiled specification source')
        if 'input_goal' in spec:
            if spec['source'] != 'gemini':
                raise ValueError('User goal requires a model-compiled specification')
            if not isinstance(spec['input_goal'], str) or not spec['input_goal'].strip() or len(spec['input_goal']) > 1000:
                raise ValueError('Invalid compiled goal text')
            origin['input_goal'] = spec['input_goal']
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
                               dataset=args.dataset, targeted_disagreement=args.targeted_disagreement,
                               direct_diversity=args.direct_diversity, rollback_monitor=args.rollback_monitor,
                               reactive_calibration=args.reactive_calibration, hybrid_device=args.hybrid_device)))


if __name__ == '__main__':
    main()
