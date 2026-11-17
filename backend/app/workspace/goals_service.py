"""Compile and preserve reviewable, bounded local goal specifications."""
import copy
import hashlib
import json
import os
import re
import tempfile
import uuid
from pathlib import Path

from app.datasets.amylase import ROOT
from app.llm.gemini_client import request_goal
from app.llm.goal_compiler import DEFAULT_SPEC
from app.llm.local_advisor import local_gemini_configuration
from app.llm.natural_goal import compile_natural_goal
from app.rewards.reward_spec import validate_spec

GOALS = ROOT / 'output/web_goals'


class GoalChanged(Exception):
    pass


def compile_and_save(goal):
    key, model = local_gemini_configuration()
    record = compile_natural_goal(goal, lambda text: request_goal(key, model, text))
    record['model'] = model
    content = (json.dumps(record, indent=2, allow_nan=False) + '\n').encode()
    GOALS.mkdir(parents=True, exist_ok=True)
    goal_id = uuid.uuid4().hex
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=GOALS, prefix='.goal-', delete=False) as file:
            temporary = Path(file.name)
            file.write(content)
            file.flush()
            os.fsync(file.fileno())
        os.link(temporary, GOALS / f'{goal_id}.json')
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return {'id': goal_id, 'sha256': hashlib.sha256(content).hexdigest(), **record}


def load_goal(goal_id, expected_sha256=None):
    if not re.fullmatch('[0-9a-f]{32}', goal_id):
        raise ValueError('Invalid goal identifier')
    try:
        content = (GOALS / f'{goal_id}.json').read_bytes()
    except FileNotFoundError as error:
        if expected_sha256 is not None:
            raise GoalChanged('Saved goal is missing') from error
        raise
    digest = hashlib.sha256(content).hexdigest()
    if expected_sha256 is not None and digest != expected_sha256:
        raise GoalChanged('Goal changed after review')
    record = json.loads(content)
    if (set(record) != {'source', 'attempts', 'specification', 'input_goal', 'model'}
            or record['source'] != 'gemini' or not isinstance(record['input_goal'], str)
            or not record['input_goal'].strip() or len(record['input_goal']) > 1000
            or not isinstance(record['model'], str) or not re.fullmatch(r'[A-Za-z0-9._-]+', record['model'])
            or not isinstance(record['attempts'], list)):
        raise ValueError('Invalid saved goal')
    spec = record['specification']
    validate_spec(spec)
    expected = copy.deepcopy(DEFAULT_SPEC)
    for name in expected['terms']:
        expected['terms'][name]['weight'] = spec['terms'][name]['weight']
    if spec != expected:
        raise ValueError('Saved goal changed fixed constraints')
    return {'id': goal_id, 'sha256': digest, **record}


def list_goals():
    if not GOALS.is_dir():
        return []
    paths = sorted(GOALS.glob('*.json'), key=lambda path: path.stat().st_mtime_ns, reverse=True)
    result = []
    for path in paths[:20]:
        try:
            result.append(load_goal(path.stem))
        except (OSError, ValueError, KeyError, TypeError):
            continue
    return result
