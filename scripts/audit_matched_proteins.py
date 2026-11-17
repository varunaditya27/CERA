#!/usr/bin/env python3
"""Reconstruct selections and repair replays for terminal matched protein runs."""
import argparse
import copy
import itertools
import json
import math
import random
from collections import Counter
from pathlib import Path

import numpy as np
from scipy.spatial.distance import cdist
from scipy.stats import norm

from app.analysis.multiprotein_evaluation import terminal_statuses, verified_record
from app.analysis.study_protocol import validate_ired_low_change, validate_low_change_pool, validate_manifests
from app.datasets.registry import dataset_source
from app.features import amylase_representations, hydro_representations, ired_representations
from app.provenance.sources import validate_recorded_sources
from audit_development_repairs import check_targets
from audit_repeated_matched import check_local, require, select_reward, signature



def check_repair_cost(spec, warning, attempt):
    terms = {'support_shift': 'distance_penalty', 'coverage': 'uncertainty_penalty',
             'disagreement': 'uncertainty_penalty', 'diversity': 'diversity_bonus'}
    require(warning in terms and attempt['term'] == terms[warning], 'Repair term mismatch')
    term = spec['terms'][attempt['term']]
    old, (low, high) = term['weight'], term['allowed_range']
    weight, cost = attempt['proposed_weight'], attempt['cost']
    require(isinstance(weight, (int, float)) and not isinstance(weight, bool) and math.isfinite(weight)
            and isinstance(cost, (int, float)) and not isinstance(cost, bool) and math.isfinite(cost)
            and any(weight == min(high, old + step) and weight > old for step in (0.25, 0.5, 1.0)),
            'Repair proposal outside allowed menu')
    require(math.isclose(cost, (weight - old) / (high - low) + 0.05, rel_tol=1e-12, abs_tol=1e-12),
            'Repair cost mismatch')



def check_repair_order(spec, method, action):
    terms = {'support_shift': 'distance_penalty', 'coverage': 'uncertainty_penalty',
             'disagreement': 'uncertainty_penalty', 'diversity': 'diversity_bonus'}
    term = terms[action['warning']]
    row = spec['terms'][term]
    old, (low, high) = row['weight'], row['allowed_range']
    values = []
    for step in (0.25, 0.5, 1.0):
        value = min(high, old + step)
        if value > old and value not in values:
            values.append(value)
    menu = [{'option': i, 'term': term, 'weight': value, 'cost': (value - old) / (high - low) + 0.05}
            for i, value in enumerate(values)]
    advice = action.get('advice')
    if method == 'gemini_repair' and menu:
        require(isinstance(advice, dict) and advice['source'] in ('gemini', 'fallback')
                and advice['options'] == menu and isinstance(advice['option'], int)
                and not isinstance(advice['option'], bool) and 0 <= advice['option'] < len(menu)
                and (advice['source'] != 'fallback' or advice['option'] == 0),
                'Invalid recorded repair advice')
        index = advice['option']
        menu = [menu[index]] + menu[:index] + menu[index + 1:]
    else:
        require(advice is None, 'Unexpected repair advice')
    attempts = action.get('attempts', [])
    require(len(attempts) <= len(menu), 'Too many repair attempts')
    for attempt, option in zip(attempts, menu):
        require(attempt['term'] == option['term'] and attempt['proposed_weight'] == option['weight'],
                'Repair attempt order mismatch')
    if action['status'] == 'retained':
        require(len(attempts) == len(menu), 'Incomplete repair menu')


def representations(dataset):
    if dataset == 'amylase':
        return amylase_representations.load_verified_representations()
    if dataset == 'ired':
        return ired_representations.load_verified_representations()
    return hydro_representations.load_verified_representations(dataset.removeprefix('hydro-'))


def audit_group(root, manifest, statuses, sequences, scores, reference, vectors, train_ids=None):
    counts = Counter()
    signatures = {i: signature(sequence, reference) for i, sequence in sequences.items()}
    local_checked = set()
    distance_checked = False
    for seed in manifest['seeds']:
        pool = sorted(sequences) if manifest['initial_pool'] == 'eligible' else train_ids
        require(pool is not None and len(pool) >= 100 and len(pool) == len(set(pool))
                and set(pool).issubset(sequences), 'Invalid initial pool')
        expected_initial = {i: scores[i] for i in random.Random(seed).sample(pool, 100)}
        for method in manifest['methods']:
            status = statuses[(seed, method)]
            if status['status'] != 'completed':
                counts[status['status']] += 1
                continue
            raw = verified_record(root / f'seed_{seed:02d}' / method / 'run.jsonl.gz', status)
            events = [json.loads(line) for line in raw.splitlines()]
            start = events[0]
            require(start['initial'] == expected_initial and start.get('initial_pool') == manifest['initial_pool']
                    and (start['seed'], start['budget'], start['batch_size'], start['max_mutations']) == (seed, 100, 10, 4)
                    and (start['data_sha256'], start['reference_sha256']) == (manifest['data_sha256'], manifest['reference_sha256']),
                    'Initial observations or settings mismatch')
            setup = next(e['settings'] for e in events if e['event'] == 'method')
            require(setup['dataset'] == manifest['dataset'], 'Dataset mismatch')
            if method != 'random':
                validate_recorded_sources(setup['source_sha256'], manifest['code_sha256'])
                require(setup['role_seed'] == 2000 + seed and setup['member_seed'] == 3000 + seed
                        and setup.get('stop_on_failed_repairs', True) is True
                        and setup.get('bypass_evidence_gate', False) is False
                        and setup.get('disabled_repair_terms', []) == []
                        and setup.get('universal_penalty', False) is False
                        and setup.get('apply_last_rejected', False) is False
                        and setup['cache_sha256'] == manifest['representation_cache_sha256']
                        and setup['reserved_ids'] == sorted(random.Random(2000 + seed).sample(sorted(expected_initial), 20)),
                        'Predictor configuration mismatch')
            known, spec = dict(expected_initial), copy.deepcopy(setup.get('reward_spec'))
            randomizer, member_gen = random.Random(1000 + seed), random.Random(3000 + seed)
            pending = warning = target = distance = acquisition = local = stop = None
            ranges = ids = None
            for event in events[1:]:
                if event['event'] == 'method':
                    settings = event['settings']
                    if 'member_seeds' in settings:
                        require(settings['member_seeds'] == member_gen.sample(range(2**32), 5)
                                and set(settings['fitting_ids']) == set(known) - set(setup['reserved_ids']),
                                'Fitting or member seed mismatch')
                    if 'reward_distance' in settings:
                        distance = settings['reward_distance']['distances']
                    if 'acquisition_scores' in settings:
                        acquisition = settings
                    if 'local_search_proposal' in settings:
                        local = settings
                    if 'disagreement_target_evidence' in settings:
                        require(pending is None and target is None, 'Target chronology mismatch')
                        target = settings['disagreement_target_evidence']
                    if 'repair_actions' in settings:
                        require(pending is None and ranges is not None, 'Repair chronology mismatch')
                        for action in settings['repair_actions']:
                            if action['status'] in ('accepted', 'retained'):
                                check_repair_order(spec, method, action)
                            for attempt in action.get('attempts', []):
                                check_repair_cost(spec, action['warning'], attempt)
                                revised = copy.deepcopy(spec)
                                revised['terms'][attempt['term']]['weight'] = attempt['proposed_weight']
                                replay = select_reward(revised, sorted(ranges), sequences, ranges, distance, len(ids))
                                verification = attempt['verification']
                                require(replay == verification['replayed_ids'], 'Repair replay mismatch')
                                checks = verification['checks']
                                if manifest['direct_diversity'] and action['warning'] == 'diversity':
                                    differences = [sum(a != b for a, b in zip(sequences[i], sequences[j]))
                                                   for i, j in itertools.combinations(replay, 2)]
                                    resolved = None if not differences else sum(differences) / len(differences) >= 2
                                    require(checks['diversity_resolved'] == resolved, 'Diversity resolution mismatch')
                                else:
                                    require(checks['counterexamples_displaced'] == (not set(replay) & set(action['targets'])),
                                            'Repair displacement mismatch')
                                require(verification['accepted'] == all(value is True for value in checks.values()),
                                        'Repair acceptance mismatch')
                                counts['repair_replays'] += 1
                            if action['status'] == 'accepted':
                                require(action['attempts'] and action['attempts'][-1]['verification']['accepted']
                                        and not any(item['verification']['accepted'] for item in action['attempts'][:-1])
                                        and action['specification'] == revised, 'Accepted repair mismatch')
                                spec = action['specification']
                            elif action['status'] == 'retained':
                                require(action['specification'] == spec and not any(
                                    item['verification']['accepted'] for item in action['attempts']), 'Retained repair mismatch')
                elif event['event'] == 'warning' and event['type'] == 'disagreement':
                    require(pending is None, 'Warning chronology mismatch')
                    warning = event
                elif event['event'] == 'selection':
                    require(pending is None and stop is None, 'Selection chronology mismatch')
                    ids = event['ids']
                    remaining = set(sequences) - set(known)
                    require(ids and len(ids) <= 10 and len(ids) == len(set(ids)) and set(ids).issubset(remaining),
                            'Invalid selection')
                    if method == 'random':
                        require(ids == randomizer.sample(sorted(remaining), len(ids)), 'Random selection mismatch')
                    else:
                        ranges = event['prediction_ranges']
                        require(set(ranges) == remaining and warning is not None, 'Prediction pool or warning missing')
                        if method == 'greedy':
                            expected = sorted(remaining, key=lambda i: (-ranges[i]['mean'], i))[:len(ids)]
                        elif method in ('ucb', 'ei'):
                            require(acquisition is not None and acquisition['acquisition_best'] == max(known.values())
                                    and set(acquisition['acquisition_scores']) == remaining, 'Acquisition evidence mismatch')
                            calculated = {}
                            for i in remaining:
                                mean, spread = ranges[i]['mean'], ranges[i]['spread']
                                delta = mean - max(known.values())
                                value = (mean + spread if method == 'ucb' else max(delta, 0) if spread == 0
                                         else max(delta * norm.cdf(delta / spread) + spread * norm.pdf(delta / spread), 0))
                                require(math.isclose(acquisition['acquisition_scores'][i], value, rel_tol=1e-10, abs_tol=1e-12),
                                        'Acquisition value mismatch')
                                calculated[i] = value
                            expected = sorted(remaining, key=lambda i: (-calculated[i], i))[:len(ids)]
                        elif method in ('genetic', 'adalead'):
                            require(local is not None and set(local['local_search_proposal']['proposals']).issubset(remaining),
                                    'Local proposal mismatch')
                            if method not in local_checked:
                                check_local(method, known, local['local_search_known_predictions'],
                                            local['local_search_candidate_predictions'], local['local_search_proposal'],
                                            sequences, signatures, reference)
                                local_checked.add(method)
                                counts['representative_local_rounds'] += 1
                            expected = sorted(local['local_search_proposal']['proposals'],
                                              key=lambda i: (-ranges[i]['mean'], i))[:len(ids)]
                        else:
                            require(distance is not None and set(distance) == remaining, 'Distance pool mismatch')
                            if not distance_checked:
                                known_matrix = np.asarray([vectors[i] for i in sorted(known)], dtype=float)
                                pairwise = cdist(known_matrix, known_matrix)
                                np.fill_diagonal(pairwise, np.inf)
                                scale = pairwise.min(axis=1).max()
                                ordered = sorted(remaining)
                                matrix = np.asarray([vectors[i] for i in ordered], dtype=float)
                                expected_dist = np.minimum(cdist(matrix, known_matrix).min(axis=1) / scale, 1)
                                require(np.allclose(expected_dist, [distance[i] for i in ordered], rtol=1e-10, atol=1e-12),
                                        'Distance reconstruction mismatch')
                                distance_checked = True
                                counts['representative_distance_rounds'] += 1
                            expected = select_reward(spec, sorted(remaining), sequences, ranges, distance, len(ids))
                        require(ids == expected, 'Selection ranking mismatch')
                        targeted = method in ('repair', 'gemini_repair') and manifest['targeted_disagreement']
                        if targeted:
                            terms = spec['terms']
                            group = sorted(remaining, key=lambda i: (-(ranges[i]['mean']
                                - terms['uncertainty_penalty']['weight'] * ranges[i]['spread']
                                - terms['distance_penalty']['weight'] * distance[i]), i))[:100]
                            require(target is not None, 'Missing target evidence')
                            check_targets(warning, target, ids)
                        else:
                            group = sorted(remaining, key=lambda i: (-ranges[i]['mean'], i))[:100]
                            require(target is None, 'Unexpected target evidence')
                        require(warning['identifiers'] == group, 'Disagreement group mismatch')
                        warning, target = None, None
                    pending = event
                    counts['selections'] += 1
                elif event['event'] == 'reveal':
                    require(pending is not None and pending['ids'] == list(event['measurements'])
                            and all(scores[i] == value and i not in known for i, value in event['measurements'].items()),
                            'Measurement or reveal mismatch')
                    known.update(event['measurements'])
                    require(event['remaining'] == 200 - len(known), 'Budget mismatch')
                    stop = event['stop_reason']
                    pending = None
                elif event['event'] == 'stop':
                    require(pending is None and stop is None and event['remaining'] == 200 - len(known),
                            'Invalid early stop')
                    stop = event['stop_reason']
                    if stop == 'no_neighbors':
                        require(local is not None and not local['local_search_proposal']['selected'], 'Invalid local stop')
                        if method not in local_checked:
                            check_local(method, known, local['local_search_known_predictions'],
                                        local['local_search_candidate_predictions'], local['local_search_proposal'],
                                        sequences, signatures, reference)
                            local_checked.add(method)
                            counts['representative_local_rounds'] += 1
            require(pending is None and stop in ('budget_exhausted', 'no_candidates', 'failed_repairs', 'no_neighbors'),
                    'Incomplete run')
            counts['completed'] += 1
    return dict(counts)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('roots', type=Path, nargs='+')
    parser.add_argument('--allow-partial-development', action='store_true', help='Allow a partial development audit')
    parser.add_argument('--ired-low-change', action='store_true', help='Audit the separate IRED low-change study')
    args = parser.parse_args()
    if args.ired_low_change and args.allow_partial_development:
        raise ValueError('Study and partial development scopes cannot be combined')
    groups = []
    for root in args.roots:
        manifest = json.loads((root / 'manifest.json').read_text())
        groups.append((root, manifest, terminal_statuses(root, manifest)))
    manifests = [manifest for _, manifest, _ in groups]
    if args.ired_low_change:
        validate_ired_low_change(manifests)
    else:
        validate_manifests(manifests, args.allow_partial_development)
    reports = []
    for root, manifest, statuses in groups:
        data, reference_path, loader = dataset_source(manifest['dataset'])
        sequences, scores, train, data_hash, reference_hash = loader(data, reference_path, 4)
        require((data_hash, reference_hash) == (manifest['data_sha256'], manifest['reference_sha256']), 'Source fingerprint mismatch')
        reference = ''.join(reference_path.read_text().splitlines()[1:])
        if args.ired_low_change:
            validate_low_change_pool(sequences, train, reference)
        vectors = representations(manifest['dataset']) if any(m != 'random' for m in manifest['methods']) else {}
        reports.append({'dataset': manifest['dataset'], **audit_group(root, manifest, statuses, sequences, scores, reference, vectors, train)})
    print(json.dumps({'scope': 'ired_low_change' if args.ired_low_change else
                      'development' if args.allow_partial_development else 'four_protein', 'groups': reports}, sort_keys=True))


if __name__ == '__main__':
    main()
