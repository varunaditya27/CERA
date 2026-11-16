"""Run an exploratory representation-based prediction-range pilot."""
import hashlib
import importlib.metadata
import copy
import random
import time
from pathlib import Path

from app.amylase import DATA, REFERENCE
from app.amylase_representations import CACHE, CACHE_SHA256, load_verified_representations
from app import ired, ired_representations
from app.experiment import Experiment
from app.prediction_intervals import interval_radius
from app.predictor_group import fit_group, predict_group, predict_members
from app.range_report import summarize_ranges
from app.repair_coordinator import handle_warnings
from app.reward_distance import known_distances, normalized_distances
from app.reward_selection import select_batch
from app.reward_spec import validate_spec
from app.selection import PENALTIES
from app.warning_checks import (constraint_warning, coverage_warning, disagreement_warning,
                                distance_snapshot, diversity_warning, support_warning)


def run_pilot(output_dir, seed=1, role_seed=3, member_seed=4, reward_spec=None, reward_origin=None,
              repair=False, repair_advisor=None, repair_model=None, dataset='amylase'):
    if repair and reward_spec is None:
        raise ValueError('Repair requires a reward specification')
    if repair_advisor is not None and not repair:
        raise ValueError('A repair advisor requires repair mode')
    if reward_spec is not None:
        reward_spec = copy.deepcopy(reward_spec)
        validate_spec(reward_spec)
    if dataset == 'amylase':
        data_path, reference_path, cache, cache_hash = DATA, REFERENCE, CACHE, CACHE_SHA256
        vectors = load_verified_representations()
    elif dataset == 'ired':
        data_path, reference_path = ired.DATA, ired.REFERENCE
        cache, cache_hash = ired_representations.CACHE, ired_representations.CACHE_SHA256
        vectors = ired_representations.load_verified_representations()
    else:
        raise ValueError('Unknown dataset')
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=False)
    start = time.perf_counter()
    budget = reward_spec['budget'] if reward_spec else {'rounds': 10, 'batch_size': 10}
    mutation_limit = reward_spec['hard_constraints']['max_mutations'] if reward_spec else 4
    run = Experiment(data_path, reference_path, output / 'run.jsonl', seed=seed,
                     budget=budget['rounds'] * budget['batch_size'], batch_size=budget['batch_size'],
                     max_mutations=mutation_limit)
    try:
        initial = sorted(run.revealed)
        reserved = sorted(random.Random(role_seed).sample(initial, 20))
        generator = random.Random(member_seed)
        reference = ''.join(reference_path.read_text(encoding='utf-8').splitlines()[1:])
        history = []
        round_number = 0
        failures = 0
        run.record_settings({'method': 'esm_bootstrap_ridge_reward' if reward_spec else 'esm_bootstrap_ridge_greedy',
                             'dataset': dataset,
                             'reward_spec': reward_spec, 'reward_origin': reward_origin, 'repair': repair,
                             'repair_advisor': 'gemini' if repair_advisor else 'rule_based',
                             'repair_model': repair_model,
                             'role_seed': role_seed,
                             'member_seed': member_seed, 'reserved_ids': reserved,
                             'penalties': PENALTIES, 'folds': 5, 'cv_seed': seed,
                             'cv_scoring': 'neg_mean_squared_error', 'member_count': 5,
                             'spread_ddof': 0, 'nominal_coverage': 0.9,
                             'interval': 'absolute_residual_order_statistic',
                             'cache_sha256': cache_hash,
                             'source_sha256': {name: hashlib.sha256((Path(__file__).parent / name).read_bytes()).hexdigest()
                                               for name in ('amylase.py', 'amylase_representations.py', 'experiment.py',
                                                            'predictor_group.py', 'prediction_intervals.py',
                                                            'prediction_pilot.py', 'range_report.py',
                                                            'representation_cache.py', 'representations.py', 'selection.py',
                                                            'warning_checks.py', 'reward_distance.py',
                                                            'reward_selection.py', 'reward_spec.py',
                                                            'repair_coordinator.py', 'repair_engine.py',
                                                            'repair_menu.py', 'repair_verification.py',
                                                            'repair_advisor.py', 'gemini_client.py', 'ired.py',
                                                            'ired_representations.py')},
                             'scikit_learn': importlib.metadata.version('scikit-learn'),
                             'numpy': importlib.metadata.version('numpy'),
                             'scipy': importlib.metadata.version('scipy')})
        while run.stop_reason is None:
            round_number += 1
            known = run.revealed
            fitting = sorted(set(known) - set(reserved))
            member_seeds = generator.sample(range(2**32), 5)
            models, penalty = fit_group(vectors, known, fitting, reserved, seed, member_seeds)
            calibration_predictions, _ = predict_group(models, vectors, reserved)
            radius = interval_radius(calibration_predictions, [known[identifier] for identifier in reserved])
            candidate_sequences = run.candidates
            candidates = sorted(candidate_sequences)
            means, spreads = predict_group(models, vectors, candidates)
            ranges = {identifier: {'mean': float(mean), 'spread': float(spread),
                                   'lower': float(mean - radius), 'upper': float(mean + radius)}
                      for identifier, mean, spread in zip(candidates, means, spreads)}
            count = min(budget['batch_size'], run.remaining, len(candidates))
            batch_budget = run.remaining
            if reward_spec is None:
                chosen = sorted(candidates, key=lambda identifier: (-ranges[identifier]['mean'], identifier))[:count]
            else:
                distance = normalized_distances(sorted(known), candidates, vectors)
                features = {i: {'sequence': candidate_sequences[i], 'mean': ranges[i]['mean'],
                                'spread': ranges[i]['spread'], 'distance': distance['distances'][i]}
                            for i in candidates}
                selected = select_batch(reward_spec, features, reference, run.remaining)
                chosen = [entry['id'] for entry in selected]
                run.record_settings({'round': round_number, 'reward_distance': distance,
                                     'reward_selection': selected})
            if repair:
                known_ids = sorted(known)
                known_means, known_spreads = predict_group(models, vectors, known_ids)
                known_distance = known_distances(known_ids, vectors)
                calibration = [{'lower': float(prediction - radius), 'upper': float(prediction + radius),
                                'score': known[identifier]}
                               for identifier, prediction in zip(reserved, calibration_predictions)]
                earlier = [{'mean': float(mean), 'spread': float(spread), 'distance': known_distance[identifier],
                            'score': known[identifier]}
                           for identifier, mean, spread in zip(known_ids, known_means, known_spreads)
                           if identifier not in reserved]
                run.record_settings({'round': round_number, 'repair_calibration': calibration,
                                     'repair_earlier_ids': fitting, 'repair_earlier': earlier})
            run.record_settings({'penalty': penalty, 'member_seeds': member_seeds,
                                 'fitting_ids': fitting, 'interval_radius': radius})
            constraint = constraint_warning(chosen, candidate_sequences, reference, run.remaining,
                                            batch_size=budget['batch_size'], max_mutations=mutation_limit)
            run.record_warning(round_number, constraint)
            if constraint['status'] == 'triggered':
                raise ValueError('Selected batch violates constraints')
            diversity = diversity_warning({i: candidate_sequences[i] for i in chosen})
            run.record_warning(round_number, diversity)
            mean_map = {identifier: ranges[identifier]['mean'] for identifier in candidates}
            top = sorted(candidates, key=lambda identifier: (-mean_map[identifier], identifier))[:100]
            member_values = predict_members(models, vectors, top)
            members = {identifier: [float(value) for value in member_values[:, index]]
                       for index, identifier in enumerate(top)}
            disagreement = disagreement_warning(mean_map, members)
            run.record_warning(round_number, disagreement)
            snapshot = distance_snapshot(sorted(known), chosen, vectors)
            run.record_settings({'round': round_number, 'distance_snapshot': snapshot})
            measurements = run.reveal(chosen, prediction_ranges=ranges)
            support = support_warning(snapshot, ranges, measurements)
            run.record_warning(round_number, support)
            history.extend((identifier, ranges[identifier]['lower'] <= score <= ranges[identifier]['upper'])
                           for identifier, score in measurements.items())
            coverage = coverage_warning(history)
            run.record_warning(round_number, coverage)
            if repair and run.stop_reason is None:
                warnings = {'support_shift': support, 'coverage': coverage,
                            'disagreement': disagreement, 'diversity': diversity}
                targets = {'support_shift': (support['evidence'] or {}).get('qualifying_ids', []),
                           'coverage': [i for i, value in measurements.items()
                                        if not ranges[i]['lower'] <= value <= ranges[i]['upper']],
                           'disagreement': chosen, 'diversity': chosen}
                reward_spec, failures, actions, abstain = handle_warnings(
                    reward_spec, warnings, targets, features, reference, batch_budget, calibration, earlier, failures,
                    advisor=repair_advisor)
                run.record_settings({'round': round_number, 'repair_actions': actions,
                                     'consecutive_failures': failures})
                if abstain:
                    run.stop_early('failed_repairs')
    finally:
        run.close()
    rows = summarize_ranges(output / 'run.jsonl', output / 'coverage.csv')
    return {'batches': len(rows), 'seconds': time.perf_counter() - start, 'cache': str(cache)}
