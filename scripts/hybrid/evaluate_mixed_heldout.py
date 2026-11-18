#!/usr/bin/env python3
"""Check frozen prediction identities, then score held-out split predictions."""
import argparse
import hashlib
import importlib.metadata
import json
import math
import random
from pathlib import Path
from statistics import median

from scipy.stats import spearmanr

from app.datasets.registry import dataset_source
from app.features import hydro_representations, ired_representations
from app.provenance.sources import source_hashes
from scripts.hybrid.predict_mixed_heldout import DATASETS, SOURCES
from app.predictors.hybrid_predictor import hybrid_configuration


def evaluate_run(run, train, test_ids, scores):
    seed = run['seed']
    initial = sorted(random.Random(seed).sample(train, 100))
    reserved = sorted(random.Random(2000 + seed).sample(initial, 20))
    seeds = random.Random(3000 + seed).sample(range(2**32), 5)
    if run['initial_ids'] != initial or run['reserved_ids'] != reserved or run['member_seeds'] != seeds:
        raise ValueError('Training assignment mismatch')
    predictions = run['predictions']
    if [item[0] for item in predictions] != sorted(test_ids):
        raise ValueError('Held-out prediction identities mismatch')
    radius = run['radius']
    if (not isinstance(radius, (int, float)) or not math.isfinite(radius) or radius < 0
            or not math.isfinite(run['penalty']) or run['penalty'] <= 0
            or any(not isinstance(p[1], (int, float)) or not math.isfinite(p[1]) for p in predictions)):
        raise ValueError('Invalid predictions or range settings')
    actual = [scores[i] for i, _ in predictions]
    predicted = [v for _, v in predictions]
    correlation = (float(spearmanr(actual, predicted).statistic)
                   if len(set(actual)) > 1 and len(set(predicted)) > 1 else None)
    n = len(actual)
    return {'seed': seed, 'n': n, 'spearman': correlation,
            'mean_absolute_error': sum(abs(a - p) for a, p in zip(actual, predicted)) / n,
            'covered': sum(abs(a - p) <= radius for a, p in zip(actual, predicted)),
            'mean_interval_width': 2 * radius}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('predictions', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    raw = args.predictions.read_bytes()
    predictions = json.loads(raw)
    script = Path(__file__).with_name('predict_mixed_heldout.py')
    if (predictions['hybrid_configuration'] != hybrid_configuration('cuda')
            or predictions['script_sha256'] != hashlib.sha256(script.read_bytes()).hexdigest()
            or predictions['source_sha256'] != source_hashes(SOURCES)
            or predictions['versions'] != {n: importlib.metadata.version(n) for n in ('numpy', 'scipy', 'scikit-learn')}
            or [g['dataset'] for g in predictions['groups']] != list(DATASETS)):
        raise ValueError('Prediction fingerprint or group mismatch')
    result = {'predictions_sha256': hashlib.sha256(raw).hexdigest(), 'groups': []}
    for group in predictions['groups']:
        dataset = group['dataset']
        data, reference, loader = dataset_source(dataset)
        sequences, scores, train, data_hash, reference_hash = loader(data, reference, 4)
        cache_hash = (ired_representations.CACHE_SHA256 if dataset == 'ired' else
                      hydro_representations.CACHE_HASHES[dataset.removeprefix('hydro-')])
        if (group['data_sha256'] != data_hash or group['reference_sha256'] != reference_hash
                or group['cache_sha256'] != cache_hash
                or [r['seed'] for r in group['runs']] != list(range(121, 131))):
            raise ValueError('Dataset or seed mismatch')
        test_ids = sorted(set(sequences) - set(train))
        runs = [evaluate_run(run, train, test_ids, scores) for run in group['runs']]
        result['groups'].append({'dataset': dataset, 'runs': runs,
                                 'median_spearman': median([r['spearman'] for r in runs if r['spearman'] is not None])
                                 if any(r['spearman'] is not None for r in runs) else None,
                                 'median_coverage': median(r['covered'] / r['n'] for r in runs),
                                 'median_mae': median(r['mean_absolute_error'] for r in runs)})
    with args.output.open('x', encoding='utf-8') as file:
        json.dump(result, file, indent=2, allow_nan=False)
        file.write('\n')


if __name__ == '__main__':
    main()
