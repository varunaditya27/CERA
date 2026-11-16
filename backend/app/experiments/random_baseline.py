"""Draw reproducible random batches from the selected protein pool."""
import random
from pathlib import Path

from app.datasets.registry import dataset_source
from app.experiments.experiment import Experiment
from app.experiments.selection import choose_random


def run_random(output_dir, seed, dataset='amylase', initial_pool='train'):
    data, reference, loader = dataset_source(dataset)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=False)
    run = Experiment(data, reference, output / 'run.jsonl', seed=seed, loader=loader, initial_pool=initial_pool)
    try:
        generator = random.Random(1000 + seed)
        run.record_settings({'method': 'random', 'selection_seed': 1000 + seed, 'dataset': dataset})
        while run.stop_reason is None:
            candidates = run.candidates
            run.reveal(choose_random(candidates, min(10, run.remaining, len(candidates)), generator))
    finally:
        run.close()
