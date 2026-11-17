#!/usr/bin/env python3
"""Independently audit saved targeted and direct-diversity development comparisons."""
import argparse
import copy
import csv
import gzip
import hashlib
import itertools
import json
import math
import random
from collections import Counter
from pathlib import Path

import numpy as np
from scipy.stats import rankdata

from app.datasets.amylase import DATA, REFERENCE
from audit_repeated_matched import require, select_reward


def digest(data):
    return hashlib.sha256(data).hexdigest()


def check_targets(warning, evidence, selected):
    require(evidence['status'] == warning['status'] and evidence['threshold'] == 0.5,
            'Disagreement status or threshold mismatch')
    group = warning['identifiers']
    if warning['status'] == 'triggered':
        values = np.array([warning['evidence']['members'][i] for i in group])
        require(values.shape == (len(group), 5) and len(group) >= 2, 'Invalid member evidence')
        ranks = rankdata(values, axis=0, method='average')
        spans = dict(zip(group, np.ptp(ranks, axis=1) / (len(group) - 1)))
        assessed = {i: float(spans[i]) for i in selected if i in spans}
        targets = [i for i in selected if i in spans and spans[i] >= 0.5]
    else:
        assessed, targets = {}, []
    require(evidence['assessed'] == assessed and evidence['targets'] == targets
            and evidence['unassessed'] == [i for i in selected if i not in assessed],
            'Disagreement target mismatch')


def check_summary(row, known, initial_count, stop, covered, widths, scores):
    best = max(known.values())
    values = sorted(scores.values(), reverse=True)
    top = values[math.ceil(len(values) * 0.01) - 1]
    require(row['status'] == 'completed' and int(row['new_measurements']) == len(known) - initial_count
            and math.isclose(float(row['best_observed']), best, abs_tol=1e-12)
            and math.isclose(float(row['pool_regret']), values[0] - best, abs_tol=1e-12)
            and row['found_top_one_percent'] == str(best >= top) and row['stop_reason'] == stop,
            'Summary result mismatch')
    require(int(row['range_count']) == len(widths) and widths and int(row['covered']) == covered
            and math.isclose(float(row['mean_range_width']), sum(widths) / len(widths), abs_tol=1e-12),
            'Summary range mismatch')


def read_source():
    reference = ''.join(REFERENCE.read_text().splitlines()[1:])
    sequences, scores, train = {}, {}, []
    with DATA.open(newline='') as file:
        for row in csv.DictReader(file):
            sequence = row['sequence']
            if sum(a != b for a, b in zip(sequence, reference)) > 4:
                continue
            identifier = digest(sequence.encode())
            require(identifier not in sequences, 'Duplicate source sequence')
            sequences[identifier], scores[identifier] = sequence, float(row['target'])
            if row['set'] == 'train':
                train.append(identifier)
    return sequences, scores, train


def audit_run(events, seed, method, sequences, scores, train, manifest, row, counts, bypass_evidence_gate=False,
              apply_last_rejected=False, rollback_monitor=False, reactive_calibration=False,
              hybrid_device=None, role_seed=None, member_seed=None):
    start = events[0]
    require(start['event'] == 'start' and (start['seed'], start['initial_count'], start['budget'],
            start['batch_size'], start['max_mutations']) == (seed, 100, 100, 10, 4), 'Invalid start')
    require(start['data_sha256'] == manifest['data_sha256'] and start['reference_sha256'] == manifest['reference_sha256'],
            'Recorded source fingerprint mismatch')
    require(start['initial'] == {i: scores[i] for i in random.Random(seed).sample(train, 100)}, 'Initial data mismatch')
    setup = next(event['settings'] for event in events if event['event'] == 'method')
    role_seed = 2000 + seed if role_seed is None else role_seed
    member_seed = 3000 + seed if member_seed is None else member_seed
    require((setup['role_seed'], setup['member_seed']) == (role_seed, member_seed), 'Seed mismatch')
    require(setup['reserved_ids'] == sorted(random.Random(role_seed).sample(sorted(start['initial']), 20)),
            'Reserved examples mismatch')
    targeted = method != 'fixed'
    direct = method == 'direct'
    require(setup.get('rollback_monitor', False) is rollback_monitor, 'Rollback monitoring mode mismatch')
    require(setup.get('reactive_calibration', False) is reactive_calibration, 'Reactive calibration mode mismatch')
    require(setup.get('hybrid_device') == hybrid_device, 'Hybrid predictor mode mismatch')
    require(not reactive_calibration or method == 'fixed', 'Reactive audit requires fixed-reward comparison')
    if rollback_monitor:
        from app.analysis.rollback_audit import audit_rollback_events
        audit_rollback_events(events)
    require(setup['targeted_disagreement'] == targeted and setup.get('direct_diversity', False) == direct
            and setup['repair'] == (method != 'fixed'),
            'Repair mode mismatch')
    known, spec = dict(start['initial']), copy.deepcopy(setup['reward_spec'])
    generator = random.Random(member_seed)
    pending = warning = target = distances = ranges = ids = None
    covered, widths, stop = 0, [], None
    calibration_ids, revealed_order, update_required = list(setup['reserved_ids']), [], None
    round_number = 0
    for event in events[1:]:
        if event['event'] == 'method':
            settings = event['settings']
            if 'member_seeds' in settings:
                require(update_required is None, 'Missing required calibration update')
                round_number += 1
                require(settings['member_seeds'] == generator.sample(range(2**32), 5)
                        and set(settings['fitting_ids']) == set(known) - set(calibration_ids), 'Fitting evidence mismatch')
                if reactive_calibration:
                    require(settings.get('calibration_ids') == calibration_ids, 'Calibration role mismatch')
                if hybrid_device is not None:
                    fitting = sorted(settings['fitting_ids'])
                    expected_validation = sorted(random.Random(seed).sample(fitting, math.ceil(len(fitting) * .2)))
                    info = settings['hybrid_fit']
                    require(info['validation_ids'] == expected_validation and
                            info['training_ids'] == sorted(set(fitting) - set(expected_validation)) and
                            len(info['members']) == 2 and
                            [m['seed'] for m in info['members']] == settings['member_seeds'][3:] and
                            all(1 <= m['best_epoch'] <= m['epochs'] <= 200 and
                                math.isfinite(m['best_validation_mse_normalized']) and
                                m['best_validation_mse_normalized'] >= 0 for m in info['members']) and
                            math.isfinite(settings['hybrid_fit_seconds']) and settings['hybrid_fit_seconds'] >= 0,
                            'Hybrid fitting roles or member metadata mismatch')
            if 'calibration_update' in settings:
                update = settings['calibration_update']
                require(reactive_calibration and update_required == round_number and settings['round'] == round_number
                        and update == {'previous_ids': calibration_ids, 'new_ids': sorted(revealed_order[-20:]),
                                       'active_from_round': round_number + 1}, 'Calibration update mismatch')
                calibration_ids, update_required = update['new_ids'], None
            if 'reward_distance' in settings:
                distances = settings['reward_distance']['distances']
            if 'disagreement_target_evidence' in settings:
                require(pending is None and target is None, 'Target chronology error')
                target = settings['disagreement_target_evidence']
            if rollback_monitor:
                for item in settings.get('rollback_events', []):
                    if item['status'] == 'rolled_back':
                        require(spec == item['current'], 'Rollback current specification mismatch')
                        spec = item['previous']
            if 'repair_actions' in settings:
                require(pending is None and ranges is not None, 'Repair chronology error')
                for action in settings['repair_actions']:
                    for attempt in action.get('attempts', []):
                        proposed = copy.deepcopy(spec)
                        proposed['terms'][attempt['term']]['weight'] = attempt['proposed_weight']
                        replay = select_reward(proposed, sorted(ranges), sequences, ranges, distances, len(ids))
                        verification = attempt['verification']
                        require(replay == verification['replayed_ids'], 'Repair replay mismatch')
                        checks = verification['checks']
                        if direct and action['warning'] == 'diversity':
                            differences = [sum(a != b for a, b in zip(sequences[i], sequences[j]))
                                           for i, j in itertools.combinations(replay, 2)]
                            result = None if not differences else sum(differences) / len(differences) >= 2
                            require(checks['diversity_resolved'] == result, 'Diversity resolution mismatch')
                        else:
                            require(checks['counterexamples_displaced'] == (not set(replay).intersection(action['targets'])),
                                    'Repair displacement mismatch')
                        require(verification['accepted'] == all(v is True for v in checks.values()), 'Repair acceptance mismatch')
                        counts['repair_replays'] += 1
                    if action['status'] == 'accepted':
                        final = action['attempts'][-1]['verification'] if action['attempts'] else {}
                        applied = (final.get('checks', {}).get('allowed_change_and_constraints') is True
                                   if bypass_evidence_gate else final.get('accepted') is True)
                        require(action['attempts'] and applied
                                and action['specification'] == proposed, 'Accepted repair lacks successful attempt')
                        spec = action['specification']
                    elif action['status'] == 'retained':
                        require(all(not (item['verification']['checks']['allowed_change_and_constraints']
                                        if bypass_evidence_gate else item['verification']['accepted'])
                                    for item in action['attempts'])
                                and action['specification'] == spec, 'Retained repair mismatch')
                    elif action['status'] == 'applied_rejected':
                        require(apply_last_rejected and action['attempts']
                                and all(not item['verification']['accepted'] for item in action['attempts'])
                                and action['attempts'][-1]['verification']['checks']['allowed_change_and_constraints'] is True
                                and action['specification'] == proposed, 'Invalid rejected repair application')
                        spec = action['specification']
        elif event['event'] == 'warning' and event['type'] == 'coverage':
            if reactive_calibration and event['status'] == 'triggered' and stop is None:
                update_required = round_number
        elif event['event'] == 'warning' and event['type'] == 'disagreement':
            require(pending is None, 'Warning chronology error')
            warning = event
        elif event['event'] == 'selection':
            require(pending is None and stop is None and warning is not None and distances is not None, 'Selection chronology error')
            ids, ranges = event['ids'], event['prediction_ranges']
            remaining = set(sequences) - set(known)
            require(ids and len(ids) <= 10 and len(ids) == len(set(ids)) and set(ids).issubset(remaining)
                    and set(ranges) == remaining and set(distances) == remaining, 'Invalid candidate pool')
            require(ids == select_reward(spec, sorted(remaining), sequences, ranges, distances, len(ids)), 'Selection mismatch')
            terms = spec['terms']
            if targeted:
                group = sorted(remaining, key=lambda i: (-(ranges[i]['mean'] - terms['uncertainty_penalty']['weight'] * ranges[i]['spread']
                                                          - terms['distance_penalty']['weight'] * distances[i]), i))[:100]
                require(target is not None, 'Missing pre-reveal targets')
                check_targets(warning, target, ids)
            else:
                group = sorted(remaining, key=lambda i: (-ranges[i]['mean'], i))[:100]
                require(target is None, 'Unexpected target evidence')
            require(warning['identifiers'] == group, 'Disagreement group mismatch')
            pending, warning, target = event, None, None
            counts['selections'] += 1
        elif event['event'] == 'reveal':
            require(pending is not None and stop is None and pending['ids'] == list(event['measurements']), 'Reveal chronology error')
            for identifier, value in event['measurements'].items():
                require(identifier not in known and scores[identifier] == value, 'Measurement mismatch')
                bounds = pending['prediction_ranges'][identifier]
                covered += bounds['lower'] <= value <= bounds['upper']
                widths.append(bounds['upper'] - bounds['lower'])
            known.update(event['measurements'])
            revealed_order.extend(event['measurements'])
            require(event['remaining'] == 200 - len(known), 'Budget mismatch')
            stop = event['stop_reason']
            pending = None
        elif event['event'] == 'stop':
            require(pending is None and stop is None and event['remaining'] == 200 - len(known), 'Stop chronology mismatch')
            stop = event['stop_reason']
    require(pending is None and update_required is None and stop in ('failed_repairs', 'budget_exhausted', 'no_candidates'), 'Incomplete run')
    check_summary(row, known, 100, stop, covered, widths, scores)
    counts['runs'] += 1
    return start['initial']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    args = parser.parse_args()
    manifest = json.loads((args.root / 'manifest.json').read_text())
    require(manifest['data_sha256'] == digest(DATA.read_bytes()) and manifest['reference_sha256'] == digest(REFERENCE.read_bytes()),
            'Source fingerprint mismatch')
    with (args.root / 'summary.csv').open(newline='') as file:
        rows = list(csv.DictReader(file))
    summaries = {(int(row['seed']), row['method']): row for row in rows}
    require(len(rows) == len(summaries) == len(manifest['methods']), 'Missing or duplicate summary')
    keys = set(manifest['methods'])
    expected_targeted = {f'{seed}:{method}' for seed in range(31, 36) for method in ('fixed', 'targeted')}
    expected_direct = {f'{seed}:{method}' for seed in range(41, 46) for method in ('strict', 'direct')}
    require(keys in (expected_targeted, expected_direct), 'Unexpected comparison methods or seeds')
    require(manifest['specification_sha256'] == digest(Path('research/reward_spec_example.json').read_bytes()),
            'Reward specification fingerprint mismatch')
    sequences, scores, train = read_source()
    counts = Counter()
    initials = {}
    for key, state in manifest['methods'].items():
        seed_text, method = key.split(':')
        seed = int(seed_text)
        require(method in ('fixed', 'targeted', 'strict', 'direct') and state['status'] == 'completed', 'Invalid run status')
        blob = (args.root / f'seed_{seed:02d}' / method / 'run.jsonl.gz').read_bytes()
        raw = gzip.decompress(blob)
        require(digest(blob) == state['gzip_sha256'] and digest(raw) == state['uncompressed_sha256'], 'Run fingerprint mismatch')
        events = [json.loads(line) for line in raw.splitlines()]
        initial = audit_run(events, seed, method, sequences, scores, train, manifest, summaries[(seed, method)], counts)
        if seed in initials:
            require(initial == initials[seed], 'Paired initial observations differ')
        initials[seed] = initial
    print(json.dumps(dict(counts), sort_keys=True))


if __name__ == '__main__':
    main()
