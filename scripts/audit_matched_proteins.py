#!/usr/bin/env python3
"""Reconstruct selections and repair replays for terminal matched protein runs."""
import argparse
import copy
import gzip
import itertools
import json
import math
import random
from collections import Counter
from pathlib import Path

import numpy as np
from scipy.spatial.distance import cdist
from scipy.stats import norm

from app.analysis.multiprotein_evaluation import digest, terminal_statuses
from app.datasets.registry import dataset_source
from app.features import amylase_representations, hydro_representations, ired_representations
from audit_development_repairs import check_targets
from audit_repeated_matched import check_local, require, select_reward, signature


def representations(dataset):
    if dataset == 'amylase':
        return amylase_representations.load_verified_representations()
    if dataset == 'ired':
        return ired_representations.load_verified_representations()
    return hydro_representations.load_verified_representations(dataset.removeprefix('hydro-'))


def audit_group(root, manifest, statuses, sequences, scores, reference, vectors):
    counts = Counter()
    signatures = {i: signature(sequence, reference) for i, sequence in sequences.items()}
    local_checked = set()
    distance_checked = False
    for seed in manifest['seeds']:
        expected_initial = {i: scores[i] for i in random.Random(seed).sample(sorted(sequences), 100)}
        for method in manifest['methods']:
            status = statuses[(seed, method)]
            if status['status'] != 'completed':
                counts[status['status']] += 1
                continue
            blob = (root / f'seed_{seed:02d}' / method / 'run.jsonl.gz').read_bytes()
            raw = gzip.decompress(blob)
            require(digest(blob) == status['gzip_sha256'] and digest(raw) == status['uncompressed_sha256'],
                    'Run fingerprint mismatch')
            events = [json.loads(line) for line in raw.splitlines()]
            start = events[0]
            require(start['initial'] == expected_initial and start.get('initial_pool') == 'eligible'
                    and (start['seed'], start['budget'], start['batch_size'], start['max_mutations']) == (seed, 100, 10, 4)
                    and (start['data_sha256'], start['reference_sha256']) == (manifest['data_sha256'], manifest['reference_sha256']),
                    'Initial observations or settings mismatch')
            setup = next(e['settings'] for e in events if e['event'] == 'method')
            require(setup['dataset'] == manifest['dataset'], 'Dataset mismatch')
            if method != 'random':
                require(setup['role_seed'] == 2000 + seed and setup['member_seed'] == 3000 + seed
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
                            for attempt in action.get('attempts', []):
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
                                        and action['specification'] == revised, 'Accepted repair mismatch')
                                spec = action['specification']
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
    args = parser.parse_args()
    groups = []
    for root in args.roots:
        manifest = json.loads((root / 'manifest.json').read_text())
        groups.append((root, manifest, terminal_statuses(root, manifest)))
    datasets = {manifest['dataset'] for _, manifest, _ in groups}
    require(len(datasets) == len(groups), 'Duplicate protein group')
    expected = {'ired', 'hydro-P06241', 'hydro-P01053', 'hydro-P0A9X9'}
    require(args.allow_partial_development or datasets == expected, 'Full audit requires all four protein groups')
    signature = lambda m: (m['seeds'], m['methods'], m['targeted_disagreement'], m['direct_diversity'], m['specification_sha256'])
    require(all(signature(m) == signature(groups[0][1]) for _, m, _ in groups[1:]), 'Protein comparison settings differ')
    reports = []
    for root, manifest, statuses in groups:
        data, reference_path, loader = dataset_source(manifest['dataset'])
        sequences, scores, _, data_hash, reference_hash = loader(data, reference_path, 4)
        require((data_hash, reference_hash) == (manifest['data_sha256'], manifest['reference_sha256']), 'Source fingerprint mismatch')
        reference = ''.join(reference_path.read_text().splitlines()[1:])
        vectors = representations(manifest['dataset']) if any(m != 'random' for m in manifest['methods']) else {}
        reports.append({'dataset': manifest['dataset'], **audit_group(root, manifest, statuses, sequences, scores, reference, vectors)})
    print(json.dumps({'scope': 'development' if args.allow_partial_development else 'four_protein', 'groups': reports}, sort_keys=True))


if __name__ == '__main__':
    main()
