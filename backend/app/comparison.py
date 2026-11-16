"""Run and summarize a matched exploratory comparison."""
import csv
import hashlib
import importlib.metadata
import json
import random
from pathlib import Path

from app.amylase import DATA, REFERENCE
from app.experiment import Experiment
from app.selection import PENALTIES, choose_greedy, choose_random


def summarize(log_path, output_path):
    events = [json.loads(line) for line in Path(log_path).read_text(encoding='utf-8').splitlines()]
    start = events[0]
    best = max(start['initial'].values())
    rows = [(0, best)]
    for event in events:
        if event['event'] == 'reveal':
            best = max(best, *event['measurements'].values())
            rows.append((start['budget'] - event['remaining'], best))
    with Path(output_path).open('x', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['new_measurements', 'best_observed_score'])
        writer.writerows(rows)
    return rows


def run_comparison(output_dir, seed=1, selection_seed=2, role_seed=3):
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=False)
    for method in ('random', 'greedy'):
        run = Experiment(DATA, REFERENCE, output / f'{method}.jsonl', seed=seed)
        try:
            initial = sorted(run.revealed)
            reserved = set(random.Random(role_seed).sample(initial, 20))
            generator = random.Random(selection_seed)
            run.record_settings({'method': method, 'selection_seed': selection_seed,
                                 'role_seed': role_seed, 'reserved_ids': sorted(reserved),
                                 'penalties': PENALTIES, 'folds': 5, 'cv_scoring': 'neg_mean_squared_error',
                                 'encoding': 'fixed 20-amino-acid indicators by position',
                                 'source_sha256': {name: hashlib.sha256((Path(__file__).parent / name).read_bytes()).hexdigest()
                                                   for name in ('amylase.py', 'experiment.py', 'selection.py', 'comparison.py')},
                                 'scikit_learn': importlib.metadata.version('scikit-learn'),
                                 'numpy': importlib.metadata.version('numpy'),
                                 'scipy': importlib.metadata.version('scipy')})
            while run.stop_reason is None:
                candidates = run.candidates
                count = min(10, run.remaining, len(candidates))
                if method == 'random':
                    run.reveal(choose_random(candidates, count, generator))
                else:
                    scores = {identifier: score for identifier, score in run.revealed.items()
                              if identifier not in reserved}
                    ids, predictions, alpha = choose_greedy(run.revealed_sequences, scores, candidates, count, seed)
                    run.record_settings({'round_penalty': alpha})
                    run.reveal(ids, predictions)
        finally:
            run.close()
        summarize(output / f'{method}.jsonl', output / f'{method}.csv')
