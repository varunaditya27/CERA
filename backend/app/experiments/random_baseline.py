"""Draw a reproducible random batch from the restricted amylase pool."""
import random
from pathlib import Path

from app.datasets.amylase import DATA, REFERENCE
from app.experiments.experiment import Experiment
from app.experiments.selection import choose_random


def run_random(output_dir, seed):
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=False)
    run = Experiment(DATA, REFERENCE, output / 'run.jsonl', seed=seed)
    try:
        generator = random.Random(1000 + seed)
        run.record_settings({'method': 'random', 'selection_seed': 1000 + seed})
        while run.stop_reason is None:
            candidates = run.candidates
            run.reveal(choose_random(candidates, min(10, run.remaining, len(candidates)), generator))
    finally:
        run.close()
