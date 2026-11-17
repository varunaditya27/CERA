"""Reconstruct local reward selections and repair replays from saved evidence."""
import copy
import math
import random

import numpy as np
from scipy.spatial.distance import cdist

from app.provenance.sources import PILOT_SOURCE_NAMES, source_hashes
from app.rewards.reward_spec import validate_spec


def require(condition, message):
    if not condition:
        raise ValueError(message)


def rank_batch(spec, identifiers, sequences, ranges, distances, count):
    terms = spec['terms']
    matrix = np.asarray([list(sequences[i].encode('ascii')) for i in identifiers], dtype=np.uint8)
    base = np.asarray([ranges[i]['mean'] - terms['uncertainty_penalty']['weight'] * ranges[i]['spread']
                       - terms['distance_penalty']['weight'] * distances[i] for i in identifiers])
    require(np.isfinite(base).all(), 'Nonfinite recorded reward inputs')
    selected = []
    for _ in range(count):
        diversity = np.zeros(len(identifiers)) if not selected else cdist(matrix, matrix[selected], metric='hamming').min(axis=1)
        values = base + terms['diversity_bonus']['weight'] * diversity
        values[selected] = -np.inf
        selected.append(int(np.argmax(values)))
    return [identifiers[index] for index in selected]


def audit_decisions(events, sequences, scores, train, vectors, cache_hash):
    start = events[0]
    setup = next(event['settings'] for event in events if event['event'] == 'method')
    require(setup['source_sha256'] == source_hashes(PILOT_SOURCE_NAMES), 'Recorded source code differs')
    if setup.get('hybrid_device') is not None:
        require(setup['hybrid_source_sha256'] == source_hashes(('hybrid_predictor.py',)), 'Recorded mixed predictor code differs')
    require(setup['cache_sha256'] == cache_hash and setup['role_seed'] == 3 and setup['member_seed'] == 4
            and setup['acquisition'] is None and setup['local_search'] is None
            and not setup['targeted_disagreement'] and not setup['direct_diversity']
            and setup['stop_on_failed_repairs'] and not setup['bypass_evidence_gate']
            and not setup['disabled_repair_terms'] and not setup['universal_penalty']
            and not setup['apply_last_rejected'] and not setup['rollback_monitor']
            and not setup['reactive_calibration'],
            'Cache or role settings differ')
    require(start['initial_pool'] == 'train' and start['initial'] == {
        i: scores[i] for i in random.Random(start['seed']).sample(train, start['initial_count'])}, 'Initial observations differ')
    known = dict(start['initial'])
    reserved = sorted(random.Random(3).sample(sorted(known), 20))
    require(setup['reserved_ids'] == reserved, 'Reserved observations differ')
    spec = copy.deepcopy(setup['reward_spec'])
    validate_spec(spec)
    generator = random.Random(4)
    distance = saved_selection = ranges = selected = None
    selection_count = repair_count = 0
    fit_ready = False
    for event in events[1:]:
        if event['event'] == 'method':
            settings = event['settings']
            if 'member_seeds' in settings:
                require(not fit_ready, 'Duplicate fitting evidence')
                distance = saved_selection = None
                fit_ready = True
                require(settings['member_seeds'] == generator.sample(range(2**32), 5)
                        and settings['fitting_ids'] == sorted(set(known) - set(reserved)), 'Fitting roles or seeds differ')
            if 'reward_distance' in settings:
                distance = settings['reward_distance']
                saved_selection = settings['reward_selection']
            if 'repair_actions' in settings:
                require(ranges is not None and selected is not None, 'Repair has no preceding batch')
                identifiers = sorted(ranges)
                for action in settings['repair_actions']:
                    require(action['status'] in ('accepted', 'retained', 'recheck_not_triggered', 'no_replayed_targets'),
                            'Unsupported repair status')
                    attempts = action.get('attempts', [])
                    require(action['status'] in ('accepted', 'retained') or not attempts, 'Unexpected repair attempts')
                    revised = None
                    for attempt in attempts:
                        revised = copy.deepcopy(spec)
                        revised['terms'][attempt['term']]['weight'] = attempt['proposed_weight']
                        validate_spec(revised)
                        replay = rank_batch(revised, identifiers, sequences, ranges, distance['distances'], len(selected))
                        verification = attempt['verification']
                        require(replay == verification['replayed_ids'], 'Repair replay differs')
                        checks = verification['checks']
                        require(checks['counterexamples_displaced'] == (not set(replay) & set(action['targets']))
                                and verification['accepted'] == all(value is True for value in checks.values()),
                                'Repair displacement or acceptance differs')
                        repair_count += 1
                    if action['status'] == 'accepted':
                        require(attempts and attempts[-1]['verification']['accepted']
                                and not any(a['verification']['accepted'] for a in attempts[:-1])
                                and action['specification'] == revised, 'Accepted repair differs')
                        spec = revised
                    elif action['status'] == 'retained':
                        require(action['specification'] == spec and not any(a['verification']['accepted'] for a in attempts),
                                'Retained repair differs')
        elif event['event'] == 'selection':
            selected, ranges = event['ids'], event['prediction_ranges']
            identifiers = sorted(set(sequences) - set(known))
            require(fit_ready and distance is not None and set(ranges) == set(identifiers)
                    and set(distance['distances']) == set(identifiers), 'Candidate pool differs')
            for value in ranges.values():
                require(set(value) == {'mean', 'spread', 'lower', 'upper'}
                        and all(isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x) for x in value.values())
                        and value['spread'] >= 0 and value['lower'] <= value['mean'] <= value['upper'],
                        'Invalid recorded prediction range')
            known_vectors = np.asarray([vectors[i] for i in sorted(known)], dtype=np.float64)
            pairwise = cdist(known_vectors, known_vectors)
            np.fill_diagonal(pairwise, np.inf)
            scale = float(pairwise.min(axis=1).max())
            require(math.isfinite(scale) and scale > 0 and math.isclose(scale, distance['scale'], rel_tol=1e-10, abs_tol=1e-12),
                    'Distance scale differs')
            candidate_vectors = np.asarray([vectors[i] for i in identifiers], dtype=np.float64)
            actual_distances = np.minimum(cdist(candidate_vectors, known_vectors).min(axis=1) / scale, 1)
            require(np.allclose(actual_distances, [distance['distances'][i] for i in identifiers], rtol=1e-10, atol=1e-12),
                    'Candidate distances differ')
            expected = rank_batch(spec, identifiers, sequences, ranges, distance['distances'], len(selected))
            require(selected == expected and selected == [entry['id'] for entry in saved_selection], 'Batch ranking differs')
            selection_count += 1
            fit_ready = False
        elif event['event'] == 'reveal':
            known.update(event['measurements'])
    require(not fit_ready and selection_count > 0, 'Incomplete fitting or selection evidence')
    return {'selections_checked': selection_count, 'repair_replays_checked': repair_count,
            'predictors_refitted': False, 'recorded_predictions_used': True}
