#!/usr/bin/env python3
"""Evaluate the existing predictor across Amylase's capped position split."""
import argparse
import hashlib
import json
import random
from importlib.metadata import version
from pathlib import Path
from statistics import median

from app.analysis.heldout_prediction import predict_heldout
from app.datasets.amylase import DATA, REFERENCE, load_amylase
from app.features.amylase_representations import CACHE_SHA256, load_verified_representations
from app.provenance.sources import source_hashes
from evaluate_heldout_shifts import evaluate_run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    sequences, scores, train, data_hash, reference_hash = load_amylase(DATA, REFERENCE, 4)
    test_ids = sorted(set(sequences) - set(train))
    vectors = load_verified_representations()
    predictions = []
    for seed in range(121, 131):
        initial = random.Random(seed).sample(train, 100)
        training_scores = {identifier: scores[identifier] for identifier in initial}
        predictions.append(predict_heldout(vectors, training_scores, test_ids, seed))
    runs = [evaluate_run(run, train, test_ids, scores) for run in predictions]
    result = {
        'scope': 'exploratory Amylase close-to-far static prediction',
        'max_substitutions': 4, 'eligible_train': len(train), 'eligible_test': len(test_ids),
        'data_sha256': data_hash, 'reference_sha256': reference_hash, 'cache_sha256': CACHE_SHA256,
        'script_sha256': {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in
                          (Path(__file__), Path(__file__).with_name('evaluate_heldout_shifts.py'))},
        'app_sha256': source_hashes(('heldout_prediction.py', 'predictor_group.py', 'prediction_intervals.py',
                                     'amylase_representations.py', 'flip2.py')),
        'versions': {name: version(name) for name in ('numpy', 'scipy', 'scikit-learn')},
        'prediction_sha256': hashlib.sha256(json.dumps(predictions, allow_nan=False).encode()).hexdigest(),
        'median_coverage': median(row['covered'] / row['n'] for row in runs),
        'median_rank_correlation': median(row['spearman'] for row in runs if row['spearman'] is not None),
        'median_mae': median(row['mean_absolute_error'] for row in runs),
        'runs': runs,
    }
    with args.output.open('x', encoding='utf-8') as file:
        json.dump(result, file, indent=2, allow_nan=False)
        file.write('\n')


if __name__ == '__main__':
    main()
