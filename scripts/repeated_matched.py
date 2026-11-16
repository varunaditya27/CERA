#!/usr/bin/env python3
"""Run or resume the predeclared ten-seed amylase development comparison."""
import argparse
import csv
import gzip
import hashlib
import json
import os
import platform
import time
from pathlib import Path
from importlib.metadata import version

from dotenv import dotenv_values

from app.analysis.repeated_evaluation import evaluate_repeated
from app.datasets.amylase import DATA, REFERENCE, load_amylase
from app.experiments.repeated_runs import METHODS, run_one
from app.llm.gemini_client import request_repair
from app.llm.repair_advisor import advise_repair
from app.rewards.reward_spec import validate_spec

SEEDS = tuple(range(21, 31))
ROOT = Path(__file__).resolve().parents[1]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def write_json(path, value):
    temporary = path.with_suffix('.tmp')
    with temporary.open('x', encoding='utf-8') as file:
        json.dump(value, file, indent=2, allow_nan=False)
        file.write('\n')
        file.flush()
        os.fsync(file.fileno())
    temporary.replace(path)


def write_csv(path, rows, columns):
    with path.open('x', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('--resume', action='store_true')
    args = parser.parse_args()
    spec_bytes = (ROOT / 'research/reward_spec_example.json').read_bytes()
    specification = json.loads(spec_bytes)
    validate_spec(specification)
    settings = dotenv_values(ROOT / 'backend/.env')
    key = os.environ.get('GEMINI_API_KEY') or settings.get('GEMINI_API_KEY')
    model = os.environ.get('GEMINI_MODEL') or settings.get('GEMINI_MODEL')
    code_paths = sorted((ROOT / 'backend/app').rglob('*.py')) + [Path(__file__).resolve()]
    manifest = {'seeds': SEEDS, 'methods': METHODS, 'specification_sha256': digest(spec_bytes),
                'data_sha256': digest(DATA.read_bytes()), 'reference_sha256': digest(REFERENCE.read_bytes()),
                'gemini_model': model, 'python': platform.python_version(),
                'versions': {name: version(name) for name in ('numpy', 'scipy', 'scikit-learn', 'python-dotenv')},
                'code_sha256': {str(path.relative_to(ROOT)): digest(path.read_bytes()) for path in code_paths}}
    manifest = json.loads(json.dumps(manifest))
    manifest_path = args.output / 'manifest.json'
    if args.resume:
        if json.loads(manifest_path.read_text(encoding='utf-8')) != manifest:
            raise ValueError('Cannot resume with changed inputs or implementation')
    else:
        args.output.mkdir(parents=True, exist_ok=False)
        write_json(manifest_path, manifest)
    advisor = lambda kind, menu: advise_repair(lambda warning, options: request_repair(key, model, warning, options),
                                               kind, menu)
    for seed in SEEDS:
        seed_dir = args.output / f'seed_{seed:02d}'
        seed_dir.mkdir(exist_ok=True)
        for method in METHODS:
            path = seed_dir / method
            status_path = path / 'status.json'
            if status_path.exists():
                continue
            if path.exists():
                write_json(status_path, {'status': 'interrupted'})
                print(json.dumps({'seed': seed, 'method': method, 'status': 'interrupted'}), flush=True)
                continue
            started = time.perf_counter()
            try:
                run_one(path, seed, method, specification, advisor=advisor, model=model)
                raw = (path / 'run.jsonl').read_bytes()
                with (path / 'run.jsonl.gz').open('xb') as file:
                    with gzip.GzipFile(filename='', mode='wb', fileobj=file, mtime=0) as compressed:
                        compressed.write(raw)
                blob = (path / 'run.jsonl.gz').read_bytes()
                if gzip.decompress(blob) != raw:
                    raise ValueError('Record compression verification failed')
                status = {'status': 'completed', 'elapsed_seconds': time.perf_counter() - started,
                          'uncompressed_sha256': digest(raw), 'gzip_sha256': digest(blob)}
                write_json(status_path, status)
                (path / 'run.jsonl').unlink()
            except Exception as error:
                path.mkdir(exist_ok=True)
                status = {'status': 'failed', 'error_type': type(error).__name__,
                          'elapsed_seconds': time.perf_counter() - started}
                write_json(status_path, status)
            print(json.dumps({'seed': seed, 'method': method, 'status': status['status']}), flush=True)
    if (args.output / 'summary.csv').exists():
        if not (args.output / 'curves.csv').exists():
            raise ValueError('Partial evaluation output requires inspection')
        print('Existing evaluation retained; no files replaced.', flush=True)
        return
    _, scores, train, data_hash, reference_hash = load_amylase(DATA, REFERENCE, 4)
    summaries, curves = evaluate_repeated(args.output, SEEDS, METHODS, scores, set(train), data_hash,
                                           reference_hash, specification)
    columns = ('seed', 'method', 'status', 'new_measurements', 'best_observed', 'pool_regret',
               'found_top_one_percent', 'stop_reason', 'covered', 'range_count', 'mean_range_width',
               'advice_gemini', 'advice_fallback', 'advice_request_attempts', 'advice_reported_tokens',
               'elapsed_seconds')
    write_csv(args.output / 'summary.csv', summaries, columns)
    write_csv(args.output / 'curves.csv', curves,
              ('seed', 'method', 'new_measurements', 'best_observed', 'pool_regret', 'found_top_one_percent'))
    print(json.dumps({'evaluation': 'completed', 'runs': len(summaries),
                      'incomplete': sum(row['status'] != 'completed' for row in summaries)}), flush=True)


if __name__ == '__main__':
    main()
