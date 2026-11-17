#!/usr/bin/env python3
"""Compile the supported fitness goal with Gemini or a checked fallback."""
import argparse
import json
import os
from pathlib import Path

from dotenv import dotenv_values

from app.llm.gemini_client import request_goal, request_weights
from app.llm.goal_compiler import compile_goal
from app.llm.natural_goal import compile_natural_goal


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path, help='New JSON file for the specification and decision record')
    parser.add_argument('--goal', help='Fitness-maximization goal text; sent to Gemini and saved in the record')
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('Output already exists')
    settings = dotenv_values(Path(__file__).resolve().parents[1] / 'backend' / '.env')
    api_key = os.environ.get('GEMINI_API_KEY') or settings.get('GEMINI_API_KEY')
    model = os.environ.get('GEMINI_MODEL') or settings.get('GEMINI_MODEL')
    result = (compile_goal(lambda: request_weights(api_key, model)) if args.goal is None else
              compile_natural_goal(args.goal, lambda goal: request_goal(api_key, model, goal)))
    result['model'] = model
    with args.output.open('x', encoding='utf-8') as file:
        json.dump(result, file, indent=2, allow_nan=False)
        file.write('\n')
    print(json.dumps({'source': result['source'], 'attempts': result['attempts'], 'model': model}))


if __name__ == '__main__':
    main()
