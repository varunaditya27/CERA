#!/usr/bin/env python3
"""Independently audit the completed repeated amylase development records."""
import argparse
import copy
import csv
import gzip
import hashlib
import itertools
import json
import math
import random
import sys
from pathlib import Path

import numpy as np
from dotenv import dotenv_values
from scipy.spatial.distance import cdist
from scipy.stats import norm

from app.datasets.amylase import DATA, REFERENCE
from app.features.amylase_representations import load_verified_representations
from app.provenance.audit_output import write_new_or_confirm_saved


def require(condition, message):
    if not condition:
        raise ValueError(message)


def select_reward(spec, ids, sequences, ranges, distances, count):
    terms = spec['terms']
    matrix = np.asarray([list(sequences[i].encode()) for i in ids], dtype=np.uint8)
    means = np.asarray([ranges[i]['mean'] for i in ids])
    spreads = np.asarray([ranges[i]['spread'] for i in ids])
    distance_values = np.asarray([distances[i] for i in ids])
    base = (means - terms['uncertainty_penalty']['weight'] * spreads
            - terms['distance_penalty']['weight'] * distance_values)
    picked = []
    for _ in range(count):
        diversity = np.zeros(len(ids)) if not picked else cdist(matrix, matrix[picked], metric='hamming').min(axis=1)
        scores = base + terms['diversity_bonus']['weight'] * diversity
        scores[picked] = -np.inf
        picked.append(int(np.argmax(scores)))
    return [ids[index] for index in picked]


def signature(sequence, reference):
    return {position: residue for position, residue in enumerate(sequence) if residue != reference[position]}


def mutation_distance(left, right, reference):
    return sum(right.get(k, reference[k]) != v for k, v in left.items()) + sum(k not in left for k in right)


def check_local(method, known, known_predictions, predictions, proposal, sequences, signatures, reference):
    parents = sorted(known, key=lambda identifier: (-known[identifier], identifier))[:10]
    if method == 'adalead':
        best = known[parents[0]]
        parents = [i for i in parents if known[i] >= best - 0.05 * abs(best)]
    require(parents == proposal['parents'], 'Local parent mismatch')
    candidates = sorted(predictions)
    if method == 'genetic':
        recombinants = {sequences[i] for i in parents}
        for left, right in itertools.permutations([sequences[i] for i in parents], 2):
            for position, (a, b) in enumerate(zip(left, right)):
                if a != b and position + 1 < len(reference):
                    recombinants.add(left[:position + 1] + right[position + 1:])
        recomb_signatures = [signature(sequence, reference) for sequence in recombinants]
        expected = [i for i in candidates
                    if any(mutation_distance(signatures[i], signatures[p], reference) <= 2 for p in parents)
                    and any(mutation_distance(signatures[i], s, reference) <= 1 for s in recomb_signatures)]
    else:
        all_predictions = {**known_predictions, **predictions}
        expected_set = set()
        for parent in parents:
            expected_set.update(i for i in candidates if mutation_distance(signatures[i], signatures[parent], reference) == 1)
            intermediate = [i for i in all_predictions if mutation_distance(signatures[i], signatures[parent], reference) == 1
                            and all_predictions[i] >= known_predictions[parent]]
            expected_set.update(i for i in candidates
                                if mutation_distance(signatures[i], signatures[parent], reference) <= 2
                                and any(mutation_distance(signatures[i], signatures[x], reference) == 1 for x in intermediate))
        expected = sorted(expected_set)
    require(expected == proposal['proposals'], 'Local proposal set mismatch')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    parser.add_argument('--report', type=Path, help='New audit-report path (default: inside the run directory)')
    args = parser.parse_args()
    root = args.root
    manifest = json.loads((root / 'manifest.json').read_text())
    require(manifest['data_sha256'] == hashlib.sha256(DATA.read_bytes()).hexdigest(), 'Source fingerprint mismatch')
    require(manifest['reference_sha256'] == hashlib.sha256(REFERENCE.read_bytes()).hexdigest(), 'Reference fingerprint mismatch')
    reference = ''.join(REFERENCE.read_text().splitlines()[1:])
    sequences, scores, train = {}, {}, []
    with DATA.open(newline='') as file:
        for row in csv.DictReader(file):
            sequence = row['sequence']
            if sum(a != b for a, b in zip(sequence, reference)) > 4:
                continue
            identifier = hashlib.sha256(sequence.encode()).hexdigest()
            sequences[identifier], scores[identifier] = sequence, float(row['target'])
            if row['set'] == 'train':
                train.append(identifier)
    signatures = {i: signature(sequence, reference) for i, sequence in sequences.items()}
    values = sorted(scores.values(), reverse=True)
    optimum, threshold = values[0], values[math.ceil(len(values) * 0.01) - 1]
    vectors = load_verified_representations()
    with (root / 'summary.csv').open(newline='') as file:
        summaries = {(int(row['seed']), row['method']): row for row in csv.DictReader(file)}
    with (root / 'curves.csv').open(newline='') as file:
        curve_rows = list(csv.DictReader(file))
    key = dotenv_values(Path(__file__).resolve().parents[2] / 'backend/.env').get('GEMINI_API_KEY')
    counts = {'runs': 0, 'selections': 0, 'repair_replays': 0, 'representative_local_rounds': 0,
              'representative_distance_rounds': 0, 'model_advice': 0}
    source_hashes = {Path(path).name: value for path, value in manifest['code_sha256'].items() if path.startswith('backend/app/')}
    for seed in manifest['seeds']:
        shared_initial = None
        for method in manifest['methods']:
            path = root / f'seed_{seed:02d}' / method
            status = json.loads((path / 'status.json').read_text())
            require(status['status'] == 'completed', 'Run is not completed')
            blob = (path / 'run.jsonl.gz').read_bytes()
            require(hashlib.sha256(blob).hexdigest() == status['gzip_sha256'], 'Compressed fingerprint mismatch')
            raw = gzip.decompress(blob)
            require(hashlib.sha256(raw).hexdigest() == status['uncompressed_sha256'], 'Record fingerprint mismatch')
            require(not key or key.encode() not in raw, 'Credential found in run record')
            events = [json.loads(line) for line in raw.splitlines()]
            start = events[0]
            expected_initial = {i: scores[i] for i in random.Random(seed).sample(train, 100)}
            require(start['initial'] == expected_initial, 'Initial measurement mismatch')
            require((start['seed'], start['budget'], start['batch_size'], start['max_mutations']) == (seed, 100, 10, 4),
                    'Starting configuration mismatch')
            require(start['data_sha256'] == manifest['data_sha256'] and start['reference_sha256'] == manifest['reference_sha256'],
                    'Run source fingerprint mismatch')
            if shared_initial is None:
                shared_initial = start['initial']
            require(start['initial'] == shared_initial, 'Methods did not share initial measurements')
            setup = next(e['settings'] for e in events if e['event'] == 'method')
            if method != 'random':
                require(setup.get('rollback_monitor', False) is False and setup.get('reactive_calibration', False) is False and setup.get('hybrid_device') is None, 'Experimental rollback monitoring is not part of this study')
                require(setup['role_seed'] == 2000 + seed and setup['member_seed'] == 3000 + seed,
                        'Model seed mismatch')
                expected_reserved = sorted(random.Random(2000 + seed).sample(sorted(start['initial']), 20))
                require(setup['reserved_ids'] == expected_reserved, 'Range-setting assignment mismatch')
                require(all(source_hashes.get(name) == value for name, value in setup['source_sha256'].items()),
                        'Recorded implementation fingerprint mismatch')
            known = dict(start['initial'])
            spec = copy.deepcopy(setup.get('reward_spec'))
            randomizer = random.Random(1000 + seed)
            member_generator = random.Random(3000 + seed)
            pending = reward_evidence = acquisition = local = None
            covered = 0
            widths = []
            observed_curve = [(0, max(known.values()))]
            stop = None
            for event in events[1:]:
                if event['event'] == 'method':
                    settings = event['settings']
                    if 'member_seeds' in settings:
                        require(settings['member_seeds'] == member_generator.sample(range(2**32), 5),
                                'Predictor member seed sequence mismatch')
                        require(set(settings['fitting_ids']) == set(known) - set(setup['reserved_ids']),
                                'Predictor fitting data mismatch')
                    if 'reward_distance' in settings:
                        reward_evidence = settings
                    if 'acquisition_scores' in settings:
                        acquisition = settings
                    if 'local_search_proposal' in settings:
                        local = settings
                        require(set(local['local_search_known_predictions']) == set(known), 'Local known predictions mismatch')
                        require(set(local['local_search_candidate_predictions']) == set(sequences) - set(known), 'Local pool mismatch')
                        parents = sorted(known, key=lambda i: (-known[i], i))[:10]
                        if method == 'adalead':
                            best = known[parents[0]]
                            parents = [i for i in parents if known[i] >= best - 0.05 * abs(best)]
                        require(parents == local['local_search_proposal']['parents'], 'Local parent mismatch')
                        if seed in (21, 30):
                            check_local(method, known, local['local_search_known_predictions'],
                                        local['local_search_candidate_predictions'], local['local_search_proposal'],
                                        sequences, signatures, reference)
                            counts['representative_local_rounds'] += 1
                    if 'repair_actions' in settings:
                        for action in settings['repair_actions']:
                            for attempt in action.get('attempts', []):
                                revised = copy.deepcopy(spec)
                                revised['terms'][attempt['term']]['weight'] = attempt['proposed_weight']
                                ids = sorted(last_ranges)
                                replayed = select_reward(revised, ids, sequences, last_ranges,
                                                         reward_evidence['reward_distance']['distances'], len(last_ids))
                                require(replayed == attempt['verification']['replayed_ids'], 'Repair replay mismatch')
                                require(attempt['verification']['checks']['counterexamples_displaced'] ==
                                        (not set(replayed).intersection(action['targets'])), 'Repair displacement mismatch')
                                counts['repair_replays'] += 1
                            if action.get('advice'):
                                advice = action['advice']
                                require(all(set(option) == {'option', 'term', 'weight', 'cost'} for option in advice['options']),
                                        'Advisor received unexpected option fields')
                                require(0 <= advice['option'] < len(advice['options']), 'Invalid advice index')
                                counts['model_advice'] += 1
                            if action['status'] == 'accepted':
                                spec = action['specification']
                elif event['event'] == 'selection':
                    require(pending is None and stop is None, 'Selection chronology error')
                    ids = event['ids']
                    remaining_ids = set(sequences) - set(known)
                    require(ids and len(ids) <= 10 and len(ids) == len(set(ids)) and set(ids).issubset(remaining_ids),
                            'Invalid selected identifiers')
                    if method == 'random':
                        require(ids == randomizer.sample(sorted(remaining_ids), len(ids)), 'Random selection mismatch')
                    else:
                        ranges = event['prediction_ranges']
                        require(set(ranges) == remaining_ids, 'Candidate prediction pool mismatch')
                        if method == 'greedy':
                            expected = sorted(ranges, key=lambda i: (-ranges[i]['mean'], i))[:len(ids)]
                        elif method in ('ucb', 'ei'):
                            require(acquisition['acquisition_best'] == max(known.values()), 'Acquisition incumbent mismatch')
                            observed = acquisition['acquisition_scores']
                            require(set(observed) == remaining_ids, 'Acquisition pool mismatch')
                            for i, row in ranges.items():
                                mean, spread = row['mean'], row['spread']
                                delta = mean - max(known.values())
                                value = (mean + spread if method == 'ucb' else max(delta, 0) if spread == 0
                                         else delta * norm.cdf(delta / spread) + spread * norm.pdf(delta / spread))
                                require(math.isclose(observed[i], value, rel_tol=1e-10, abs_tol=1e-12), 'Acquisition value mismatch')
                            expected = sorted(observed, key=lambda i: (-observed[i], i))[:len(ids)]
                        elif method in ('genetic', 'adalead'):
                            proposal = local['local_search_proposal']
                            require(set(proposal['proposals']).issubset(remaining_ids), 'Local proposal outside pool')
                            expected = sorted(proposal['proposals'], key=lambda i: (-ranges[i]['mean'], i))[:len(ids)]
                        else:
                            distances = reward_evidence['reward_distance']['distances']
                            require(set(distances) == remaining_ids, 'Reward distance pool mismatch')
                            if seed in (21, 30) and len(known) == 100:
                                k = np.asarray([vectors[i] for i in sorted(known)], dtype=float)
                                pairs = cdist(k, k)
                                np.fill_diagonal(pairs, np.inf)
                                scale = pairs.min(axis=1).max()
                                ids_sorted = sorted(remaining_ids)
                                candidate_vectors = np.asarray([vectors[i] for i in ids_sorted], dtype=float)
                                normalized = np.minimum(cdist(candidate_vectors, k).min(axis=1) / scale, 1)
                                require(np.allclose(normalized, [distances[i] for i in ids_sorted], rtol=1e-10, atol=1e-12),
                                        'Distance reconstruction mismatch')
                                counts['representative_distance_rounds'] += 1
                            expected = select_reward(spec, sorted(remaining_ids), sequences, ranges, distances, len(ids))
                        require(ids == expected, 'Selection ranking mismatch')
                        last_ranges = ranges
                    last_ids = ids
                    pending = event
                    counts['selections'] += 1
                elif event['event'] == 'reveal':
                    require(pending is not None and pending['ids'] == list(event['measurements']), 'Reveal chronology mismatch')
                    for identifier, value in event['measurements'].items():
                        require(identifier not in known and scores[identifier] == value, 'Revealed source score mismatch')
                        if 'prediction_ranges' in pending:
                            bounds = pending['prediction_ranges'][identifier]
                            covered += bounds['lower'] <= value <= bounds['upper']
                            widths.append(bounds['upper'] - bounds['lower'])
                    known.update(event['measurements'])
                    require(event['remaining'] == 100 - len(known) + 100, 'Budget mismatch')
                    observed_curve.append((len(known) - 100, max(known.values())))
                    stop = event['stop_reason']
                    pending = None
                elif event['event'] == 'stop':
                    require(pending is None and stop is None and event['remaining'] == 200 - len(known), 'Early stop mismatch')
                    if event['stop_reason'] == 'no_neighbors':
                        require(local is not None and not local['local_search_proposal']['selected'], 'Invalid local stop')
                    stop = event['stop_reason']
            row = summaries[(seed, method)]
            require(pending is None and stop == row['stop_reason'], 'Incomplete or mismatched stop')
            count, best = observed_curve[-1]
            require(int(row['new_measurements']) == count and math.isclose(float(row['best_observed']), best)
                    and math.isclose(float(row['pool_regret']), optimum - best, abs_tol=1e-12)
                    and (row['found_top_one_percent'] == str(best >= threshold)), 'Summary mismatch')
            require(int(row['range_count']) == len(widths), 'Coverage denominator mismatch')
            if widths:
                require(int(row['covered']) == covered and math.isclose(float(row['mean_range_width']), sum(widths) / len(widths)),
                        'Coverage or width mismatch')
            else:
                require(not row['covered'] and not row['mean_range_width'], 'Unavailable coverage incorrectly reported')
            actual_curve = [(int(row['new_measurements']), float(row['best_observed'])) for row in curve_rows
                            if int(row['seed']) == seed and row['method'] == method]
            require(actual_curve == observed_curve, 'Saved curve mismatch')
            counts['runs'] += 1
        print(json.dumps({'seed': seed, 'status': 'audited'}), flush=True)
    require(counts['runs'] == len(manifest['seeds']) * len(manifest['methods']), 'Missing runs')
    counts['audit_script_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    output = args.report if args.report is not None else root / 'independent_audit.json'
    status = write_new_or_confirm_saved(output, counts)
    print(json.dumps(counts), flush=True)
    print(f'Audit {status}.', file=sys.stderr)


if __name__ == '__main__':
    main()
