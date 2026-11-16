"""Run an exploratory representation-based prediction-range pilot."""
import hashlib
import importlib.metadata
import random
import time
from pathlib import Path

from app.amylase import DATA, REFERENCE
from app.amylase_representations import CACHE, CACHE_SHA256, load_verified_representations
from app.experiment import Experiment
from app.prediction_intervals import interval_radius
from app.predictor_group import fit_group, predict_group
from app.range_report import summarize_ranges
from app.selection import PENALTIES


def run_pilot(output_dir, seed=1, role_seed=3, member_seed=4):
    vectors = load_verified_representations()
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=False)
    start = time.perf_counter()
    run = Experiment(DATA, REFERENCE, output / 'run.jsonl', seed=seed)
    try:
        initial = sorted(run.revealed)
        reserved = sorted(random.Random(role_seed).sample(initial, 20))
        generator = random.Random(member_seed)
        run.record_settings({'method': 'esm_bootstrap_ridge_greedy', 'role_seed': role_seed,
                             'member_seed': member_seed, 'reserved_ids': reserved,
                             'penalties': PENALTIES, 'folds': 5, 'cv_seed': seed,
                             'cv_scoring': 'neg_mean_squared_error', 'member_count': 5,
                             'spread_ddof': 0, 'nominal_coverage': 0.9,
                             'interval': 'absolute_residual_order_statistic',
                             'cache_sha256': CACHE_SHA256,
                             'source_sha256': {name: hashlib.sha256((Path(__file__).parent / name).read_bytes()).hexdigest()
                                               for name in ('amylase.py', 'amylase_representations.py', 'experiment.py',
                                                            'predictor_group.py', 'prediction_intervals.py',
                                                            'prediction_pilot.py', 'range_report.py',
                                                            'representation_cache.py', 'representations.py', 'selection.py')},
                             'scikit_learn': importlib.metadata.version('scikit-learn'),
                             'numpy': importlib.metadata.version('numpy'),
                             'scipy': importlib.metadata.version('scipy')})
        while run.stop_reason is None:
            known = run.revealed
            fitting = sorted(set(known) - set(reserved))
            member_seeds = generator.sample(range(2**32), 5)
            models, penalty = fit_group(vectors, known, fitting, reserved, seed, member_seeds)
            calibration_predictions, _ = predict_group(models, vectors, reserved)
            radius = interval_radius(calibration_predictions, [known[identifier] for identifier in reserved])
            candidates = sorted(run.candidates)
            means, spreads = predict_group(models, vectors, candidates)
            ranges = {identifier: {'mean': float(mean), 'spread': float(spread),
                                   'lower': float(mean - radius), 'upper': float(mean + radius)}
                      for identifier, mean, spread in zip(candidates, means, spreads)}
            count = min(10, run.remaining, len(candidates))
            chosen = sorted(candidates, key=lambda identifier: (-ranges[identifier]['mean'], identifier))[:count]
            run.record_settings({'penalty': penalty, 'member_seeds': member_seeds,
                                 'fitting_ids': fitting, 'interval_radius': radius})
            run.reveal(chosen, prediction_ranges=ranges)
    finally:
        run.close()
    rows = summarize_ranges(output / 'run.jsonl', output / 'coverage.csv')
    return {'batches': len(rows), 'seconds': time.perf_counter() - start, 'cache': str(CACHE)}
