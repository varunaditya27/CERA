"""Validate and evaluate terminal matched searches for one protein group."""
import gzip
import hashlib
import json
import math
import random
from collections import Counter
from pathlib import Path

from app.analysis.recovery import summarize_recovery
from app.experiments.evaluation import evaluate
from app.experiments.repeated_runs import METHODS
from app.provenance.sources import validate_recorded_sources


def digest(data):
    return hashlib.sha256(data).hexdigest()



def verified_record(path, status):
    blob = Path(path).read_bytes()
    if digest(blob) != status['gzip_sha256']:
        raise ValueError('Compressed run fingerprint mismatch')
    raw = gzip.decompress(blob)
    if digest(raw) != status['uncompressed_sha256']:
        raise ValueError('Uncompressed run fingerprint mismatch')
    return raw


def repair_costs(actions):
    costs = []
    for action in actions:
        attempts = action.get('attempts', [])
        for attempt in attempts:
            cost, accepted = attempt['cost'], attempt['verification']['accepted']
            if (isinstance(cost, bool) or not isinstance(cost, (int, float)) or not math.isfinite(cost)
                    or cost < 0 or not isinstance(accepted, bool)):
                raise ValueError('Invalid recorded repair cost or acceptance')
            costs.append({'warning': action['warning'], 'term': attempt['term'],
                          'proposed_weight': attempt['proposed_weight'], 'cost': cost, 'accepted': accepted})
        accepted = [attempt['verification']['accepted'] for attempt in attempts]
        if ((action['status'] == 'accepted' and (not accepted or not accepted[-1] or any(accepted[:-1])))
                or (action['status'] != 'accepted' and any(accepted))):
            raise ValueError('Recorded repair acceptance mismatch')
    return costs


def terminal_statuses(root, manifest):
    seeds, methods = manifest['seeds'], manifest['methods']
    if (not seeds or not methods or len(set(seeds)) != len(seeds) or len(set(methods)) != len(methods)
            or any(not isinstance(seed, int) or isinstance(seed, bool) for seed in seeds)
            or any(method not in METHODS for method in methods)
            or manifest['initial_pool'] not in ('eligible', 'train')
            or (manifest['initial_pool'] == 'train' and manifest['dataset'] != 'ired')):
        raise ValueError('Invalid matched comparison manifest')
    statuses = {}
    for seed in seeds:
        for method in methods:
            path = Path(root) / f'seed_{seed:02d}' / method / 'status.json'
            if not path.is_file():
                raise ValueError('Not all configured runs have terminal statuses')
            status = json.loads(path.read_text(encoding='utf-8'))
            if status.get('status') not in ('completed', 'failed', 'interrupted'):
                raise ValueError('Invalid or nonterminal run status')
            statuses[(seed, method)] = status
    return statuses


def evaluate_group(root, manifest, statuses, scores, data_hash, reference_hash, specification, train_ids=None,
                   sequences=None, reference=None):
    if manifest['data_sha256'] != data_hash or manifest['reference_sha256'] != reference_hash:
        raise ValueError('Dataset fingerprints do not match manifest')
    summaries, curves = [], []
    for seed in manifest['seeds']:
        pool = sorted(scores) if manifest['initial_pool'] == 'eligible' else train_ids
        if pool is None or len(pool) < 100 or len(pool) != len(set(pool)) or not set(pool).issubset(scores):
            raise ValueError('Invalid starting pool')
        expected_ids = random.Random(seed).sample(pool, 100)
        expected_initial = {i: scores[i] for i in expected_ids}
        reserved = sorted(random.Random(2000 + seed).sample(sorted(expected_ids), 20))
        shared_settings = None
        for method in manifest['methods']:
            status = statuses[(seed, method)]
            if status['status'] != 'completed':
                summaries.append({'seed': seed, 'method': method, 'status': status['status'],
                                  'error_type': status.get('error_type')})
                continue
            raw = verified_record(Path(root) / f'seed_{seed:02d}' / method / 'run.jsonl.gz', status)
            events = [json.loads(line) for line in raw.splitlines()]
            start = events[0]
            if ((start['seed'], start['initial_count'], start['budget'], start['batch_size'], start['max_mutations'],
                 start.get('initial_pool')) != (seed, 100, 100, 10, 4, manifest['initial_pool']) or start['initial'] != expected_initial):
                raise ValueError('Starting observations or settings mismatch')
            settings = next(event['settings'] for event in events if event['event'] == 'method')
            if settings['dataset'] != manifest['dataset']:
                raise ValueError('Dataset mismatch')
            if method == 'random':
                if settings['method'] != 'random' or settings['selection_seed'] != 1000 + seed:
                    raise ValueError('Random method settings mismatch')
            else:
                validate_recorded_sources(settings['source_sha256'], manifest['code_sha256'])
                expected_method = ('esm_bootstrap_ridge_' + method if method in ('ucb', 'ei', 'genetic', 'adalead') else
                                   'esm_bootstrap_ridge_reward' if method in ('fixed', 'repair', 'gemini_repair') else
                                   'esm_bootstrap_ridge_greedy')
                if (settings['method'] != expected_method or settings['cache_sha256'] != manifest['representation_cache_sha256']
                        or settings['role_seed'] != 2000 + seed or settings['member_seed'] != 3000 + seed
                        or settings['reserved_ids'] != reserved):
                    raise ValueError('Predictor settings mismatch')
                model_settings = tuple(settings[key] for key in ('penalties', 'folds', 'cv_seed', 'cv_scoring',
                                                               'member_count', 'spread_ddof', 'nominal_coverage', 'interval'))
                if shared_settings is None:
                    shared_settings = model_settings
                elif shared_settings != model_settings:
                    raise ValueError('Predictor settings differ across methods')
                uses_reward = method in ('fixed', 'repair', 'gemini_repair')
                uses_repair = method in ('repair', 'gemini_repair')
                if (settings['reward_spec'] != (specification if uses_reward else None)
                        or settings['repair'] != uses_repair
                        or settings.get('stop_on_failed_repairs', True) is not True
                        or settings.get('bypass_evidence_gate', False) is not False
                        or settings.get('disabled_repair_terms', []) != []
                        or settings['targeted_disagreement'] != (manifest['targeted_disagreement'] if uses_repair else False)
                        or settings['direct_diversity'] != (manifest['direct_diversity'] if uses_repair else False)
                        or settings['acquisition'] != (method if method in ('ucb', 'ei') else None)
                        or settings['local_search'] != (method if method in ('genetic', 'adalead') else None)):
                    raise ValueError('Method configuration mismatch')
                if uses_repair and settings['repair_advisor'] != ('gemini' if method == 'gemini_repair' else 'rule_based'):
                    raise ValueError('Repair advisor mismatch')
                if method == 'gemini_repair' and settings['repair_model'] != manifest['gemini_model']:
                    raise ValueError('Gemini model mismatch')
            result = evaluate(events, scores, set(scores), data_hash, reference_hash)
            if ((result['stop_reason'] == 'no_neighbors' and method not in ('genetic', 'adalead'))
                    or (result['stop_reason'] == 'failed_repairs' and method not in ('repair', 'gemini_repair'))):
                raise ValueError('Stop reason does not match method')
            recovery = None if method == 'random' else summarize_recovery(events)
            warnings = Counter(event['type'] for event in events if event['event'] == 'warning' and event['status'] == 'triggered')
            actions = [action for event in events if event['event'] == 'method'
                       for action in event['settings'].get('repair_actions', [])]
            advice = [action['advice'] for action in actions if action.get('advice')]
            attempts = [attempt for item in advice for attempt in item['attempts']]
            summary = {'seed': seed, 'method': method, 'status': 'completed', **result['curve'][-1],
                       'stop_reason': result['stop_reason'], 'covered': result['covered'],
                       'range_count': result['range_count'], 'mean_range_width': result['mean_range_width'],
                       'recovery': recovery, 'warning_counts': dict(warnings),
                       'repair_actions': len(actions), 'repair_attempts': sum(len(a.get('attempts', [])) for a in actions),
                       'repairs_accepted': sum(a['status'] == 'accepted' for a in actions),
                       'repair_costs': repair_costs(actions),
                       'advice_gemini': sum(item['source'] == 'gemini' for item in advice),
                       'advice_fallback': sum(item['source'] == 'fallback' for item in advice),
                       'advice_request_attempts': sum(item['status'] != 'invalid_configuration' for item in attempts),
                       'advice_reported_tokens': sum(item.get('usage', {}).get('totalTokenCount', 0) for item in attempts),
                       'elapsed_seconds': status.get('elapsed_seconds')}
            if manifest['initial_pool'] == 'train':
                if sequences is None or reference is None:
                    raise ValueError('Missing sequences or reference for mutation counts')
                selected = [identifier for event in events if event['event'] == 'selection' for identifier in event['ids']]
                summary['selected_mutation_counts'] = dict(sorted(Counter(
                    str(sum(a != b for a, b in zip(sequences[i], reference))) for i in selected).items()))
            summaries.append(summary)
            curves.extend({'seed': seed, 'method': method, **row} for row in result['curve'])
    by_run = {(row['seed'], row['method']): row for row in summaries}
    paired = []
    if 'fixed' in manifest['methods']:
        for seed in manifest['seeds']:
            baseline = by_run[(seed, 'fixed')]
            for method in manifest['methods']:
                if method == 'fixed':
                    continue
                candidate = by_run[(seed, method)]
                available = baseline['status'] == candidate['status'] == 'completed'
                paired.append({'seed': seed, 'method': method, 'baseline': 'fixed',
                               'method_status': candidate['status'], 'baseline_status': baseline['status'],
                               'best_observed_difference': (candidate['best_observed'] - baseline['best_observed']
                                                            if available else None),
                               'new_measurement_difference': (candidate['new_measurements'] - baseline['new_measurements']
                                                              if available else None)})
    return {'dataset': manifest['dataset'], 'summaries': summaries, 'curves': curves, 'paired_to_fixed': paired}
