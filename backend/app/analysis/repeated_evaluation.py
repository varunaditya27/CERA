"""Evaluate completed repeated-run records only after all methods have stopped."""
import gzip
import hashlib
import json

from app.experiments.evaluation import evaluate
from app.features.amylase_representations import CACHE_SHA256


def evaluate_repeated(root, seeds, methods, scores, train, data_hash, reference_hash, specification):
    summaries, curves = [], []
    for seed in seeds:
        initial = reserved = shared_model = None
        for method in methods:
            path = root / f'seed_{seed:02d}' / method
            status = json.loads((path / 'status.json').read_text(encoding='utf-8'))
            if status['status'] != 'completed':
                summaries.append({'seed': seed, 'method': method, 'status': status['status']})
                continue
            compressed = (path / 'run.jsonl.gz').read_bytes()
            if hashlib.sha256(compressed).hexdigest() != status['gzip_sha256']:
                raise ValueError('Compressed run fingerprint mismatch')
            raw = gzip.decompress(compressed)
            if hashlib.sha256(raw).hexdigest() != status['uncompressed_sha256']:
                raise ValueError('Run content fingerprint mismatch')
            events = [json.loads(line) for line in raw.splitlines()]
            start = events[0]
            if (start['seed'] != seed or start['initial_count'] != 100 or start['budget'] != 100
                    or start['batch_size'] != 10 or start['max_mutations'] != 4):
                raise ValueError('Run settings mismatch')
            if initial is None:
                initial = events[0]['initial']
            elif initial != events[0]['initial']:
                raise ValueError('Methods have different initial measurements')
            settings = next(e['settings'] for e in events if e['event'] == 'method')
            if method == 'random':
                if settings['method'] != 'random' or settings['selection_seed'] != 1000 + seed:
                    raise ValueError('Random method settings mismatch')
            else:
                if settings.get('rollback_monitor', False) is not False or settings.get('reactive_calibration', False) is not False or settings.get('hybrid_device') is not None:
                    raise ValueError('Experimental rollback monitoring is not part of this study')
                if settings['dataset'] != 'amylase' or settings['cache_sha256'] != CACHE_SHA256:
                    raise ValueError('Dataset or representation mismatch')
                if settings['role_seed'] != 2000 + seed or settings['member_seed'] != 3000 + seed:
                    raise ValueError('Model seed assignment mismatch')
                model_settings = tuple(settings[key] for key in ('penalties', 'folds', 'cv_seed', 'cv_scoring',
                                                               'member_count', 'spread_ddof', 'nominal_coverage', 'interval'))
                if shared_model is None:
                    shared_model = model_settings
                elif shared_model != model_settings:
                    raise ValueError('Predictor settings differ')
                if method in ('fixed', 'repair', 'gemini_repair'):
                    if settings['reward_spec'] != specification or settings['repair'] != (method != 'fixed'):
                        raise ValueError('Reward or repair settings mismatch')
                    if method == 'gemini_repair' and settings['repair_advisor'] != 'gemini':
                        raise ValueError('Gemini advisor missing')
                    if method == 'repair' and settings['repair_advisor'] != 'rule_based':
                        raise ValueError('Rule-based advisor mismatch')
                elif settings['reward_spec'] is not None or settings['repair']:
                    raise ValueError('Unexpected reward or repair')
                if settings['acquisition'] != (method if method in ('ucb', 'ei') else None):
                    raise ValueError('Acquisition settings mismatch')
                if settings['local_search'] != (method if method in ('genetic', 'adalead') else None):
                    raise ValueError('Local search settings mismatch')
                if reserved is None:
                    reserved = settings['reserved_ids']
                elif reserved != settings['reserved_ids']:
                    raise ValueError('Range-setting examples differ')
            result = evaluate(events, scores, train, data_hash, reference_hash)
            if ((result['stop_reason'] == 'no_neighbors' and method not in ('genetic', 'adalead'))
                    or (result['stop_reason'] == 'failed_repairs' and method not in ('repair', 'gemini_repair'))):
                raise ValueError('Stop reason does not match method')
            advice = [action['advice'] for event in events if event['event'] == 'method'
                      for action in event['settings'].get('repair_actions', []) if action.get('advice')]
            attempts = [attempt for item in advice for attempt in item['attempts']]
            summary = {'seed': seed, 'method': method, 'status': 'completed', **result['curve'][-1],
                       'stop_reason': result['stop_reason'], 'covered': result['covered'],
                       'range_count': result['range_count'], 'mean_range_width': result['mean_range_width'],
                       'advice_gemini': sum(item['source'] == 'gemini' for item in advice),
                       'advice_fallback': sum(item['source'] == 'fallback' for item in advice),
                       'advice_request_attempts': sum(item['status'] != 'invalid_configuration' for item in attempts),
                       'advice_reported_tokens': sum(item.get('usage', {}).get('totalTokenCount', 0)
                                                     for item in attempts),
                       'elapsed_seconds': status['elapsed_seconds']}
            summaries.append(summary)
            curves.extend({'seed': seed, 'method': method, **row} for row in result['curve'])
    return summaries, curves
