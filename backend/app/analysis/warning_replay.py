"""Reconstruct warning evidence from a historical amylase pilot record."""
import csv
import gzip
import hashlib
import importlib.metadata
import json
import subprocess
from pathlib import Path

import numpy as np

from app.datasets.amylase import DATA, REFERENCE, ROOT
from app.features.amylase_representations import CACHE_SHA256
from app.predictors.prediction_intervals import interval_radius
from app.predictors.predictor_group import fit_group, predict_group, predict_members
from app.features.representations import sequence_id
from app.provenance.sources import source_hashes
from app.rewards.warning_checks import (constraint_warning, coverage_warning, disagreement_warning,
                                distance_snapshot, diversity_warning, support_warning)

HISTORICAL_COMMIT = '78fce61'
HISTORICAL_FILES = {'amylase.py', 'amylase_representations.py', 'experiment.py', 'predictor_group.py',
                    'prediction_intervals.py', 'prediction_pilot.py', 'range_report.py',
                    'representation_cache.py', 'representations.py', 'selection.py'}


def _verify_source(settings):
    if set(settings['source_sha256']) != HISTORICAL_FILES:
        raise ValueError('Incomplete historical source fingerprints')
    for name, digest in settings['source_sha256'].items():
        if Path(name).name != name:
            raise ValueError('Invalid recorded source filename')
        source = subprocess.run(['git', 'show', f'{HISTORICAL_COMMIT}:backend/app/{name}'],
                                cwd=ROOT, capture_output=True, check=True).stdout
        if hashlib.sha256(source).hexdigest() != digest:
            raise ValueError('Historical source fingerprint mismatch')


def replay_record(source_path, output_path, vectors, on_selection=None):
    source_path = Path(source_path)
    with gzip.open(source_path, 'rt', encoding='utf-8') as file:
        events = [json.loads(line) for line in file]
    if len(events) < 2 or events[0]['event'] != 'start' or events[1]['event'] != 'method':
        raise ValueError('Invalid historical run')
    start, setup = events[0], events[1]['settings']
    _verify_source(setup)
    if (setup['cache_sha256'] != CACHE_SHA256 or
            start['data_sha256'] != hashlib.sha256(DATA.read_bytes()).hexdigest() or
            start['reference_sha256'] != hashlib.sha256(REFERENCE.read_bytes()).hexdigest()):
        raise ValueError('Historical data or cache fingerprint mismatch')
    with DATA.open(newline='', encoding='utf-8') as file:
        rows = list(csv.DictReader(file))
    sequences = {sequence_id(row['sequence']): row['sequence'] for row in rows}
    source_scores = {sequence_id(row['sequence']): float(row['target']) for row in rows}
    reference = ''.join(REFERENCE.read_text(encoding='utf-8').splitlines()[1:])
    known = dict(start['initial'])
    reserved = sorted(setup['reserved_ids'])
    if (len(reserved) != 20 or len(set(reserved)) != 20 or not set(reserved).issubset(known)
            or any(identifier not in source_scores or source_scores[identifier] != score
                   for identifier, score in known.items())):
        raise ValueError('Historical initial or reserved measurements mismatch')
    eligible = {identifier for identifier, sequence in sequences.items()
                if len(sequence) == len(reference) and
                sum(a != b for a, b in zip(sequence, reference)) <= start['max_mutations']}
    history, pending, method, round_number = [], None, None, 0
    counts = {}
    with Path(output_path).open('x', encoding='utf-8') as out:
        def write(event):
            out.write(json.dumps(event, allow_nan=False) + '\n')
            out.flush()

        def write_warning(warning):
            key = f"{warning['type']}:{warning['status']}"
            counts[key] = counts.get(key, 0) + 1
            write({'event': 'warning', 'run': str(source_path), 'round': round_number, **warning})

        write({'event': 'replay_start', 'source_record': str(source_path),
               'source_sha256': hashlib.sha256(source_path.read_bytes()).hexdigest(),
               'historical_commit': HISTORICAL_COMMIT, 'cache_sha256': CACHE_SHA256,
               'reconstruction_code_sha256': source_hashes(('warning_checks.py', 'warning_replay.py',
                                                             'predictor_group.py', 'sources.py')),
               'versions': {name: importlib.metadata.version(name) for name in ('numpy', 'scipy', 'scikit-learn')}})
        for event in events[2:]:
            if event['event'] == 'method':
                if pending is not None or method is not None:
                    raise ValueError('Unexpected method record')
                method = event['settings']
            elif event['event'] == 'selection':
                if pending is not None or method is None:
                    raise ValueError('Missing pre-reveal method record')
                round_number += 1
                fitting = method['fitting_ids']
                if set(fitting) != set(known) - set(reserved):
                    raise ValueError('Historical fitting data mismatch')
                models, penalty = fit_group(vectors, known, fitting, reserved, setup['cv_seed'], method['member_seeds'])
                if penalty != method['penalty']:
                    raise ValueError('Historical penalty mismatch')
                calibration, _ = predict_group(models, vectors, reserved)
                radius = interval_radius(calibration, [known[i] for i in reserved])
                if not np.isclose(radius, method['interval_radius'], rtol=1e-10, atol=1e-12):
                    raise ValueError('Historical interval radius mismatch')
                ranges, chosen = event['prediction_ranges'], event['ids']
                if set(ranges) != eligible - set(known):
                    raise ValueError('Invalid historical candidates')
                means = {identifier: value['mean'] for identifier, value in ranges.items()}
                ranked = sorted(means, key=lambda i: (-means[i], i))
                if chosen != ranked[:len(chosen)]:
                    raise ValueError('Historical ranking mismatch')
                top = ranked[:100]
                member_values = predict_members(models, vectors, top)
                for index, identifier in enumerate(top):
                    values = member_values[:, index]
                    if not (np.isclose(values.mean(), ranges[identifier]['mean'], rtol=1e-10, atol=1e-12)
                            and np.isclose(values.std(ddof=0), ranges[identifier]['spread'], rtol=1e-10, atol=1e-12)):
                        raise ValueError('Historical member predictions mismatch')
                if on_selection is not None:
                    on_selection(round_number, models, vectors, ranked, ranges)
                members = {identifier: [float(value) for value in member_values[:, index]]
                           for index, identifier in enumerate(top)}
                candidates = {identifier: sequences[identifier] for identifier in ranges}
                snapshot = distance_snapshot(sorted(known), chosen, vectors)
                write({'event': 'pre_reveal_evidence', 'round': round_number, 'distance_snapshot': snapshot})
                write_warning(constraint_warning(chosen, candidates, reference, start['budget'] - len(history),
                                                 start['batch_size'], start['max_mutations']))
                write_warning(diversity_warning({identifier: candidates[identifier] for identifier in chosen}))
                write_warning(disagreement_warning(means, members))
                pending = (chosen, ranges, snapshot)
            elif event['event'] == 'reveal':
                if pending is None or pending[0] != list(event['measurements']):
                    raise ValueError('Historical reveal mismatch')
                chosen, ranges, snapshot = pending
                measurements = event['measurements']
                if (set(measurements) & set(known) or
                        any(source_scores[i] != score for i, score in measurements.items()) or
                        event['remaining'] != start['budget'] - len(history) - len(chosen)):
                    raise ValueError('Historical budget or repeated measurement mismatch')
                write({'event': 'reveal_reference', 'round': round_number, 'identifiers': chosen})
                write_warning(support_warning(snapshot, ranges, measurements))
                history.extend((i, ranges[i]['lower'] <= value <= ranges[i]['upper'])
                               for i, value in measurements.items())
                write_warning(coverage_warning(history))
                known.update(measurements)
                pending, method = None, None
            else:
                raise ValueError('Unexpected historical event')
        if pending is not None or method is not None or not events[-1].get('stop_reason'):
            raise ValueError('Incomplete historical run')
        write({'event': 'replay_end', 'rounds': round_number, 'warning_counts': counts,
               'stop_reason': events[-1]['stop_reason']})
    return counts
