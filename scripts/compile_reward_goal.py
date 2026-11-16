#!/usr/bin/env python3
"""Compile the supported fitness goal with Gemini or a checked fallback."""
import argparse
import json
import os
from pathlib import Path

from dotenv import dotenv_values

from app.gemini_client import request_weights
from app.goal_compiler import compile_goal


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path, help='New JSON file for the specification and decision record')
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('Output already exists')
    settings = dotenv_values(Path(__file__).resolve().parents[1] / 'backend' / '.env')
    api_key = os.environ.get('GEMINI_API_KEY') or settings.get('GEMINI_API_KEY')
    model = os.environ.get('GEMINI_MODEL') or settings.get('GEMINI_MODEL')
    result = compile_goal(lambda: request_weights(api_key, model))
    result['model'] = model
    with args.output.open('x', encoding='utf-8') as file:
        json.dump(result, file, indent=2, allow_nan=False)
        file.write('\n')
    print(json.dumps({'source': result['source'], 'attempts': result['attempts'], 'model': model}))


if __name__ == '__main__':
    main()
