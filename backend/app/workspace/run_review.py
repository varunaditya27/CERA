"""Review completed runs without returning predictions for unselected variants."""
import json
from collections import Counter

from app.datasets.registry import dataset_source
from app.experiments.evaluation import evaluate
from app.rewards.reward_spec import validate_spec
from app.workspace import runs_service


def review_run(run_id):
    summary = runs_service.read_experiment(run_id)
    if summary['id'] != run_id:
        raise ValueError('Run identity mismatch')
    path = runs_service.RUNS / run_id / 'run.jsonl'
    events = [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines()]
    setup = next(event['settings'] for event in events if event['event'] == 'method')
    dataset = summary.get('dataset', 'amylase')
    if (setup['dataset'] != dataset or events[0]['seed'] != summary['seed']
            or setup['repair'] != summary['repair']):
        raise ValueError('Run settings mismatch')
    validate_spec(setup['reward_spec'])
    data, reference, loader = dataset_source(dataset)
    _, scores, train, data_hash, reference_hash = loader(data, reference, events[0]['max_mutations'])
    evaluation = evaluate(events, scores, set(train), data_hash, reference_hash)
    final = evaluation['curve'][-1]
    if (final['new_measurements'] != summary['new_measurements']
            or final['best_observed'] != summary['best_observed']
            or evaluation['stop_reason'] != summary['stop_reason']
            or evaluation['covered'] != summary['covered'] or evaluation['range_count'] != summary['range_count']):
        raise ValueError('Run summary mismatch')
    batches, warnings, repairs = [], {}, {}
    pending = None
    for event in events:
        if event['event'] == 'selection':
            pending = event
        elif event['event'] == 'reveal':
            rows = []
            for identifier, score in event['measurements'].items():
                ranges = pending['prediction_ranges'][identifier]
                rows.append({'id': identifier, 'score': score, 'prediction': ranges['mean'],
                             'lower': ranges['lower'], 'upper': ranges['upper']})
            batches.append({'round': len(batches) + 1, 'measurements': rows})
            pending = None
        elif event['event'] == 'warning':
            warnings.setdefault(event['round'], []).append({'type': event['type'], 'status': event['status']})
        elif event['event'] == 'method' and 'repair_actions' in event['settings']:
            settings = event['settings']
            actions = []
            for action in settings['repair_actions']:
                attempts = [{'term': attempt['term'], 'proposed_weight': attempt['proposed_weight'],
                             'accepted': attempt['verification']['accepted'],
                             'checks': attempt['verification']['checks']}
                            for attempt in action.get('attempts', [])]
                actions.append({'warning': action['warning'], 'status': action['status'], 'attempts': attempts,
                                'advice_source': (action.get('advice') or {}).get('source')})
            repairs.setdefault(settings['round'], []).extend(actions)
    if set(warnings) - set(range(1, len(batches) + 1)) or set(repairs) - set(range(1, len(batches) + 1)):
        raise ValueError('Run contains evidence outside a completed batch')
    recorded_warnings = Counter(w['type'] for items in warnings.values() for w in items if w['status'] == 'triggered')
    accepted = sum(a['status'] == 'accepted' for items in repairs.values() for a in items)
    if dict(recorded_warnings) != summary['warnings'] or accepted != summary['accepted_repairs']:
        raise ValueError('Run warning or repair summary mismatch')
    for batch in batches:
        batch['warnings'] = warnings.get(batch['round'], [])
        batch['repairs'] = repairs.get(batch['round'], [])
    return {'summary': summary, 'batches': batches, 'specification': setup['reward_spec'],
            'goal': setup['reward_origin'].get('input_goal')}
