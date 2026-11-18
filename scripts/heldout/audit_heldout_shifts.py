#!/usr/bin/env python3
"""Refit each held-out predictor and independently recalculate reported metrics."""
import argparse
import hashlib
import importlib.metadata
import json
import sys
import math
import random
from pathlib import Path

import numpy as np
from scipy.stats import rankdata

from app.datasets.registry import dataset_source
from app.predictors.predictor_group import fit_group, predict_group
from app.features import hydro_representations, ired_representations
from app.provenance.sources import CodeChanged, require_recorded_code, source_hashes
from scripts.reporting.legacy_audit import rerun_with_recorded_code
from scripts.heldout.predict_heldout_shifts import DATASETS, SOURCES


def close(left, right):
    return math.isclose(left, right, rel_tol=1e-10, abs_tol=1e-10)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('predictions', type=Path)
    parser.add_argument('evaluation', type=Path)
    args = parser.parse_args()
    raw = args.predictions.read_bytes()
    predictions, evaluation = json.loads(raw), json.loads(args.evaluation.read_text())
    script = Path(__file__).with_name('predict_heldout_shifts.py')
    if (evaluation['predictions_sha256'] != hashlib.sha256(raw).hexdigest()
            or predictions['versions'] != {n: importlib.metadata.version(n) for n in ('numpy', 'scipy', 'scikit-learn')}
            or [g['dataset'] for g in predictions['groups']] != list(DATASETS)
            or [g['dataset'] for g in evaluation['groups']] != list(DATASETS)):
        raise ValueError('Fingerprint or dataset mismatch')
    require_recorded_code(predictions['script_sha256'] == hashlib.sha256(script.read_bytes()).hexdigest(),
                          predictions['source_sha256'] == source_hashes(SOURCES))
    total_predictions = 0
    for group, reported in zip(predictions['groups'], evaluation['groups']):
        dataset = group['dataset']
        data, reference, loader = dataset_source(dataset)
        sequences, scores, train, data_hash, reference_hash = loader(data, reference, 4)
        if dataset == 'ired':
            vectors = ired_representations.load_verified_representations()
            cache_hash = ired_representations.CACHE_SHA256
        else:
            protein = dataset.removeprefix('hydro-')
            vectors = hydro_representations.load_verified_representations(protein)
            cache_hash = hydro_representations.CACHE_HASHES[protein]
        if (group['data_sha256'] != data_hash or group['reference_sha256'] != reference_hash
                or group['cache_sha256'] != cache_hash
                or [r['seed'] for r in group['runs']] != list(range(121, 131))
                or [r['seed'] for r in reported['runs']] != list(range(121, 131))):
            raise ValueError('Data or run identity mismatch')
        test_ids = sorted(set(sequences) - set(train))
        for run, metrics in zip(group['runs'], reported['runs']):
            seed = run['seed']
            initial = sorted(random.Random(seed).sample(train, 100))
            reserved = sorted(random.Random(2000 + seed).sample(initial, 20))
            fitting = sorted(set(initial) - set(reserved))
            members = random.Random(3000 + seed).sample(range(2**32), 5)
            selected = {i: scores[i] for i in initial}
            models, penalty = fit_group(vectors, selected, fitting, reserved, seed, members)
            calibration, _ = predict_group(models, vectors, reserved)
            errors = sorted(abs(scores[i] - value) for i, value in zip(reserved, calibration))
            radius = float(errors[math.ceil(21 * .9) - 1])
            means, _ = predict_group(models, vectors, test_ids)
            if (run['initial_ids'] != initial or run['reserved_ids'] != reserved or run['member_seeds'] != members
                    or not close(run['penalty'], penalty) or not close(run['radius'], radius)
                    or [p[0] for p in run['predictions']] != test_ids
                    or not np.allclose([p[1] for p in run['predictions']], means, rtol=1e-10, atol=1e-10)):
                raise ValueError('Predictor reproduction mismatch')
            actual = np.array([scores[i] for i in test_ids])
            n = len(actual)
            correlation = (float(np.corrcoef(rankdata(actual), rankdata(means))[0, 1])
                           if len(set(actual)) > 1 and len(set(means)) > 1 else None)
            error = float(np.abs(actual - means).mean())
            covered = int(np.count_nonzero(np.abs(actual - means) <= radius))
            if (metrics['n'] != n or metrics['covered'] != covered
                    or (correlation is None) != (metrics['spearman'] is None)
                    or (correlation is not None and not close(metrics['spearman'], correlation))
                    or not close(metrics['mean_absolute_error'], error)
                    or not close(metrics['mean_interval_width'], 2 * radius)):
                raise ValueError('Metric mismatch')
            total_predictions += n
        runs = reported['runs']
        ranks = [r['spearman'] for r in runs if r['spearman'] is not None]
        medians = {'median_spearman': float(np.median(ranks)) if ranks else None,
                   'median_coverage': float(np.median([r['covered'] / r['n'] for r in runs])),
                   'median_mae': float(np.median([r['mean_absolute_error'] for r in runs]))}
        if any((v is None and reported[k] is not None) or
               (v is not None and (reported[k] is None or not close(v, reported[k]))) for k, v in medians.items()):
            raise ValueError('Median mismatch')
    print(json.dumps({'checked_runs': 40, 'refitted_models': 200,
                      'checked_predictions': total_predictions}, sort_keys=True))


if __name__ == '__main__':
    try:
        main()
    except CodeChanged:
        sys.exit(rerun_with_recorded_code('audit_heldout_shifts', '2a81f24'))
