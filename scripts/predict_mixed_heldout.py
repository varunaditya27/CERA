#!/usr/bin/env python3
"""Freeze held-out split predictions before inspecting test-side outcomes."""
import argparse
import hashlib
import importlib.metadata
import json
import random
from pathlib import Path

from app.analysis.mixed_heldout_prediction import predict_mixed_heldout
from app.experiments.hybrid_predictor import hybrid_configuration
from app.datasets.registry import dataset_source
from app.features import hydro_representations, ired_representations
from app.provenance.sources import source_hashes

DATASETS = ('ired', 'hydro-P06241', 'hydro-P01053', 'hydro-P0A9X9')
SOURCES = ('mixed_heldout_prediction.py', 'hybrid_predictor.py', 'predictor_group.py', 'prediction_intervals.py', 'selection.py',
           'flip2.py', 'amylase.py', 'hydro.py', 'ired.py', 'registry.py', 'representation_cache.py',
           'representations.py', 'ired_representations.py', 'hydro_representations.py', 'sources.py')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    result = {'scope': 'exploratory static capped split; not active search',
              'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'source_sha256': source_hashes(SOURCES),
              'versions': {name: importlib.metadata.version(name) for name in ('numpy', 'scipy', 'scikit-learn')},
              'hybrid_configuration': hybrid_configuration('cuda'), 'groups': []}
    for dataset in DATASETS:
        data, reference, loader = dataset_source(dataset)
        sequences, scores, train, data_hash, reference_hash = loader(data, reference, 4)
        test_ids = sorted(set(sequences) - set(train))
        if dataset == 'ired':
            vectors = ired_representations.load_verified_representations()
            cache_hash = ired_representations.CACHE_SHA256
        else:
            protein = dataset.removeprefix('hydro-')
            vectors = hydro_representations.load_verified_representations(protein)
            cache_hash = hydro_representations.CACHE_HASHES[protein]
        group = {'dataset': dataset, 'data_sha256': data_hash, 'reference_sha256': reference_hash,
                 'cache_sha256': cache_hash, 'runs': []}
        for seed in range(121, 131):
            initial = random.Random(seed).sample(train, 100)
            selected_scores = {identifier: scores[identifier] for identifier in initial}
            group['runs'].append(predict_mixed_heldout(vectors, selected_scores, test_ids, seed, 'cuda'))
            print(f'{dataset} seed {seed} predicted', flush=True)
        result['groups'].append(group)
    with args.output.open('x', encoding='utf-8') as file:
        json.dump(result, file, allow_nan=False, separators=(',', ':'))
        file.write('\n')


if __name__ == '__main__':
    main()
