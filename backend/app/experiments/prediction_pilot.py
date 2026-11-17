"""Run an exploratory representation-based prediction-range pilot."""
import importlib.metadata
import copy
import random
import time
from pathlib import Path

from app.features.amylase_representations import CACHE, CACHE_SHA256, load_verified_representations
from app.datasets import hydro
from app.datasets.registry import dataset_source
from app.features import hydro_representations, ired_representations
from app.experiments.experiment import Experiment
from app.experiments.acquisition import acquisition_scores, choose_acquisition
from app.experiments.local_search import propose_local
from app.experiments.prediction_intervals import interval_radius
from app.experiments.predictor_group import fit_group, predict_group, predict_members
from app.experiments.range_report import summarize_ranges
from app.provenance.sources import PILOT_SOURCE_NAMES, source_hashes
from app.rewards.repair_coordinator import handle_warnings
from app.rewards.disagreement_targets import disagreement_targets
from app.rewards.reward_distance import known_distances, normalized_distances
from app.rewards.reward_selection import select_batch
from app.rewards.reward_spec import validate_spec
from app.experiments.selection import PENALTIES
from app.rewards.warning_checks import (constraint_warning, coverage_warning, disagreement_warning,
                                distance_snapshot, diversity_warning, support_warning)


def run_pilot(output_dir, seed=1, role_seed=3, member_seed=4, reward_spec=None, reward_origin=None,
              repair=False, repair_advisor=None, repair_model=None, dataset='amylase', acquisition=None,
              local_search=None, targeted_disagreement=False, direct_diversity=False, initial_pool='train'):
    if acquisition not in (None, 'ucb', 'ei') or (acquisition is not None and (reward_spec is not None or repair)):
        raise ValueError('Invalid acquisition configuration')
    if (local_search not in (None, 'genetic', 'adalead') or
            (local_search is not None and (acquisition is not None or reward_spec is not None or repair))):
        raise ValueError('Invalid local search configuration')
    if repair and reward_spec is None:
        raise ValueError('Repair requires a reward specification')
    if (targeted_disagreement or direct_diversity) and not repair:
        raise ValueError('Experimental repair checks require repair mode')
    if repair_advisor is not None and not repair:
        raise ValueError('A repair advisor requires repair mode')
    if reward_spec is not None:
        reward_spec = copy.deepcopy(reward_spec)
        validate_spec(reward_spec)
    data_path, reference_path, loader = dataset_source(dataset)
    if dataset == 'amylase':
        cache, cache_hash = CACHE, CACHE_SHA256
        vectors = load_verified_representations()
    elif dataset == 'ired':
        cache, cache_hash = ired_representations.CACHE, ired_representations.CACHE_SHA256
        vectors = ired_representations.load_verified_representations()
    elif isinstance(dataset, str) and dataset.startswith('hydro-') and dataset.removeprefix('hydro-') in hydro.PROTEINS:
        protein = dataset.removeprefix('hydro-')
        cache = hydro.ROOT / 'output/representations' / f'hydro_{protein}_esm2_c731040.npz'
        cache_hash = hydro_representations.CACHE_HASHES[protein]
        vectors = hydro_representations.load_verified_representations(protein)
    else:
        raise ValueError('Unknown dataset')
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=False)
    start = time.perf_counter()
    budget = reward_spec['budget'] if reward_spec else {'rounds': 10, 'batch_size': 10}
    mutation_limit = reward_spec['hard_constraints']['max_mutations'] if reward_spec else 4
    run = Experiment(data_path, reference_path, output / 'run.jsonl', seed=seed,
                     budget=budget['rounds'] * budget['batch_size'], batch_size=budget['batch_size'],
                     max_mutations=mutation_limit, loader=loader, initial_pool=initial_pool)
    try:
        initial = sorted(run.revealed)
        reserved = sorted(random.Random(role_seed).sample(initial, 20))
        generator = random.Random(member_seed)
        reference = ''.join(reference_path.read_text(encoding='utf-8').splitlines()[1:])
        history = []
        round_number = 0
        failures = 0
        run.record_settings({'method': ('esm_bootstrap_ridge_' + local_search if local_search else
                                       'esm_bootstrap_ridge_' + acquisition if acquisition else
                                       'esm_bootstrap_ridge_reward' if reward_spec else 'esm_bootstrap_ridge_greedy'),
                             'acquisition': acquisition, 'local_search': local_search,
                             'dataset': dataset,
                             'reward_spec': reward_spec, 'reward_origin': reward_origin, 'repair': repair,
                             'targeted_disagreement': targeted_disagreement,
                             'direct_diversity': direct_diversity,
                             'repair_advisor': 'gemini' if repair_advisor else 'rule_based',
                             'repair_model': repair_model,
                             'role_seed': role_seed,
                             'member_seed': member_seed, 'reserved_ids': reserved,
                             'penalties': PENALTIES, 'folds': 5, 'cv_seed': seed,
                             'cv_scoring': 'neg_mean_squared_error', 'member_count': 5,
                             'spread_ddof': 0, 'nominal_coverage': 0.9,
                             'interval': 'absolute_residual_order_statistic',
                             'cache_sha256': cache_hash,
                             'source_sha256': source_hashes(PILOT_SOURCE_NAMES),
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
            run.record_settings({'penalty': penalty, 'member_seeds': member_seeds,
                                 'fitting_ids': fitting, 'interval_radius': radius})
            count = min(budget['batch_size'], run.remaining, len(candidates))
            batch_budget = run.remaining
            if local_search is not None:
                known_ids = sorted(known)
                known_means, _ = predict_group(models, vectors, known_ids)
                known_predictions = {i: float(value) for i, value in zip(known_ids, known_means)}
                proposal = propose_local(local_search, run.revealed_sequences, known, known_predictions,
                                         candidate_sequences, {i: ranges[i]['mean'] for i in candidates}, count)
                run.record_settings({'round': round_number, 'local_search_proposal': proposal,
                                     'local_search_known_predictions': known_predictions,
                                     'local_search_candidate_predictions': {i: ranges[i]['mean'] for i in candidates}})
                chosen = proposal['selected']
                if not chosen:
                    run.stop_early('no_neighbors')
                    break
            elif acquisition is not None:
                scores = acquisition_scores(ranges, max(known.values()), acquisition)
                chosen = choose_acquisition(scores, count)
                run.record_settings({'round': round_number, 'acquisition_best': max(known.values()),
                                     'acquisition_scores': scores})
            elif reward_spec is None:
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
            constraint = constraint_warning(chosen, candidate_sequences, reference, run.remaining,
                                            batch_size=budget['batch_size'], max_mutations=mutation_limit)
            run.record_warning(round_number, constraint)
            if constraint['status'] == 'triggered':
                raise ValueError('Selected batch violates constraints')
            diversity = diversity_warning({i: candidate_sequences[i] for i in chosen})
            run.record_warning(round_number, diversity)
            mean_map = {identifier: ranges[identifier]['mean'] for identifier in candidates}
            if targeted_disagreement:
                terms = reward_spec['terms']
                group_scores = {i: (ranges[i]['mean'] - terms['uncertainty_penalty']['weight'] * ranges[i]['spread']
                                    - terms['distance_penalty']['weight'] * distance['distances'][i])
                                for i in candidates}
            else:
                group_scores = mean_map
            top = sorted(candidates, key=lambda identifier: (-group_scores[identifier], identifier))[:100]
            member_values = predict_members(models, vectors, top)
            members = {identifier: [float(value) for value in member_values[:, index]]
                       for index, identifier in enumerate(top)}
            disagreement = disagreement_warning(group_scores, members)
            run.record_warning(round_number, disagreement)
            if targeted_disagreement:
                target_evidence = disagreement_targets(disagreement, chosen)
                run.record_settings({'round': round_number, 'disagreement_target_evidence': target_evidence})
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
                           'disagreement': target_evidence['targets'] if targeted_disagreement else chosen,
                           'diversity': chosen}
                reward_spec, failures, actions, abstain = handle_warnings(
                    reward_spec, warnings, targets, features, reference, batch_budget, calibration, earlier, failures,
                    advisor=repair_advisor, direct_diversity=direct_diversity)
                run.record_settings({'round': round_number, 'repair_actions': actions,
                                     'consecutive_failures': failures})
                if abstain:
                    run.stop_early('failed_repairs')
    finally:
        run.close()
    rows = summarize_ranges(output / 'run.jsonl', output / 'coverage.csv')
    return {'batches': len(rows), 'seconds': time.perf_counter() - start, 'cache': str(cache)}
