"""Run a bounded local search and summarize revealed evidence."""
import fcntl
import hashlib
import json
import uuid
from pathlib import Path

from app.datasets.amylase import ROOT
from app.datasets.registry import dataset_source
from app.experiments.evaluation import evaluate

RUNS = ROOT / 'output/web_runs'
SPECIFICATION = ROOT / 'research/reward_spec_example.json'


class RunBusy(Exception):
    pass


def run_experiment(seed, repair, gemini=False, dataset='amylase', goal_id=None, goal_sha256=None):
    from app.experiments.prediction_pilot import run_pilot

    RUNS.mkdir(parents=True, exist_ok=True)
    with (RUNS / '.run.lock').open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise RunBusy from error
        advisor = model = None
        if gemini:
            from app.llm.local_advisor import local_repair_advisor
            advisor, model = local_repair_advisor()
        run_id = uuid.uuid4().hex
        directory = RUNS / run_id
        if goal_id is None:
            spec_bytes = SPECIFICATION.read_bytes()
            spec = json.loads(spec_bytes)
            origin = {'source': 'specification_file', 'input_sha256': hashlib.sha256(spec_bytes).hexdigest()}
        else:
            from app.workspace.goals_service import load_goal
            goal = load_goal(goal_id, goal_sha256)
            spec = goal['specification']
            origin = {'source': 'gemini', 'input_sha256': goal['sha256'], 'model': goal['model'], 'input_goal': goal['input_goal']}
        run_pilot(directory, seed=seed, reward_spec=spec,
                  reward_origin=origin,
                  repair=repair, repair_advisor=advisor, repair_model=model, dataset=dataset)
        events = [json.loads(line) for line in (directory / 'run.jsonl').read_text(encoding='utf-8').splitlines()]
        data, reference, loader = dataset_source(dataset)
        _, scores, train, data_hash, ref_hash = loader(data, reference, spec['hard_constraints']['max_mutations'])
        evaluation = evaluate(events, scores, set(train), data_hash, ref_hash)
        final = evaluation['curve'][-1]
        warnings = {}
        accepted = provider_attempts = provider_fallbacks = 0
        provider_tokens = provider_usage_reports = 0
        for event in events:
            if event.get('event') == 'warning' and event.get('status') == 'triggered':
                kind = event['type']
                warnings[kind] = warnings.get(kind, 0) + 1
            if event.get('event') == 'method':
                for action in event.get('settings', {}).get('repair_actions', []):
                    accepted += action.get('status') == 'accepted'
                    advice = action.get('advice')
                    if advice is not None:
                        provider_fallbacks += advice.get('source') == 'fallback'
                        for attempt in advice.get('attempts', []):
                            provider_attempts += 1
                            usage = attempt.get('usage') or {}
                            if 'totalTokenCount' in usage:
                                provider_usage_reports += 1
                                provider_tokens += usage['totalTokenCount']
        result = {'id': run_id, 'dataset': dataset, 'goal_id': goal_id, 'seed': seed, 'repair': repair, 'gemini': gemini,
                  'provider_attempts': provider_attempts, 'provider_fallbacks': provider_fallbacks,
                  'reported_total_tokens': provider_tokens if provider_usage_reports else None,
                  'provider_usage_reports': provider_usage_reports, 'new_measurements': final['new_measurements'],
                  'best_observed': final['best_observed'], 'stop_reason': evaluation['stop_reason'],
                  'covered': evaluation['covered'], 'range_count': evaluation['range_count'],
                  'mean_range_width': evaluation['mean_range_width'], 'warnings': warnings, 'accepted_repairs': accepted}
        with (directory / 'summary.json').open('x', encoding='utf-8') as file:
            json.dump(result, file, allow_nan=False, indent=2)
            file.write('\n')
        return result


def read_experiment(run_id):
    path = RUNS / run_id / 'summary.json'
    return json.loads(path.read_text(encoding='utf-8'))


def list_experiments():
    if not RUNS.is_dir():
        return []
    directories = sorted((path for path in RUNS.iterdir() if path.is_dir() and len(path.name) == 32
                          and all(c in '0123456789abcdef' for c in path.name)),
                         key=lambda path: path.stat().st_mtime_ns, reverse=True)
    results = []
    for directory in directories[:20]:
        try:
            result = read_experiment(directory.name)
            if result['id'] != directory.name:
                raise ValueError('Run identity mismatch')
            results.append({'status': 'completed', **result})
        except (OSError, ValueError, KeyError, TypeError):
            results.append({'status': 'incomplete_or_running', 'id': directory.name})
    return results
