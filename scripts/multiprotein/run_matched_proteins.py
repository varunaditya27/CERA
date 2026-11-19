#!/usr/bin/env python3
"""Run explicitly configured matched searches without evaluating hidden outcomes."""
import argparse
import gzip
import json
import os
import platform
import time
from importlib.metadata import version
from pathlib import Path

from dotenv import dotenv_values

from app.datasets import hydro
from app.analysis.study_protocol import validate_low_change_pool
from app.datasets.registry import dataset_source
from app.experiments.repeated_runs import EXTRA_METHODS, METHODS, run_one
from app.features import amylase_representations, ired_representations
from app.llm.gemini_client import request_repair
from app.llm.repair_trace import traced_repair_advice
from app.rewards.reward_spec import validate_spec
from scripts.multiprotein.repeated_matched import ROOT, digest, write_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('--dataset', required=True, choices=('amylase', 'ired', 'hydro-P06241', 'hydro-P01053', 'hydro-P0A9X9'))
    parser.add_argument('--seeds', required=True, nargs='+', type=int)
    parser.add_argument('--methods', required=True, nargs='+', choices=METHODS + EXTRA_METHODS)
    parser.add_argument('--specification', required=True, type=Path)
    parser.add_argument('--initial-pool', choices=('eligible', 'train'), default='eligible')
    parser.add_argument('--hydro-low-fitness', action='store_true',
                        help='Explicitly allow the score-defined Hydro starting pool')
    parser.add_argument('--targeted-disagreement', action='store_true')
    parser.add_argument('--direct-diversity', action='store_true')
    parser.add_argument('--resume', action='store_true')
    args = parser.parse_args()
    if args.hydro_low_fitness != (args.initial_pool == 'train' and args.dataset.startswith('hydro-')):
        raise ValueError('Hydro train starts require the explicit low-fitness flag')
    if args.initial_pool == 'train' and args.dataset != 'ired' and not args.hydro_low_fitness:
        raise ValueError('Unsupported train starting pool')
    if len(set(args.seeds)) != len(args.seeds) or len(set(args.methods)) != len(args.methods):
        raise ValueError('Seeds and methods must be unique')
    if (args.targeted_disagreement or args.direct_diversity) and not {'repair', 'gemini_repair'}.intersection(args.methods):
        raise ValueError('Repair checks require a repair method')
    spec_bytes = args.specification.read_bytes()
    spec = json.loads(spec_bytes)
    validate_spec(spec)
    if spec['budget'] != {'rounds': 10, 'batch_size': 10} or spec['hard_constraints']['max_mutations'] != 4:
        raise ValueError('Matched methods currently require the shared 100-measurement budget and four-mutation limit')
    data, reference, loader = dataset_source(args.dataset)
    if args.initial_pool == 'train' and args.dataset == 'ired':
        sequences, _, train, _, _ = loader(data, reference, 4)
        reference_sequence = ''.join(reference.read_text(encoding='utf-8').splitlines()[1:])
        validate_low_change_pool(sequences, train, reference_sequence)
    settings = dotenv_values(ROOT / 'backend/.env') if 'gemini_repair' in args.methods else {}
    key = os.environ.get('GEMINI_API_KEY') or settings.get('GEMINI_API_KEY')
    model = os.environ.get('GEMINI_MODEL') or settings.get('GEMINI_MODEL')
    if 'gemini_repair' in args.methods and (not key or not model):
        raise ValueError('Gemini repair requires a configured key and model')
    cache_hash = None
    if any(method != 'random' for method in args.methods):
        if args.dataset == 'amylase':
            cache = amylase_representations.CACHE
        elif args.dataset == 'ired':
            cache = ired_representations.CACHE
        else:
            cache = hydro.ROOT / 'output/representations' / f"hydro_{args.dataset[6:]}_esm2_c731040.npz"
        cache_hash = digest(cache.read_bytes())
    paths = sorted((ROOT / 'backend/app').rglob('*.py')) + [Path(__file__).resolve(), ROOT / 'scripts/multiprotein/repeated_matched.py']
    manifest = {'dataset': args.dataset, 'initial_pool': args.initial_pool, 'seeds': args.seeds, 'methods': args.methods,
                'targeted_disagreement': args.targeted_disagreement, 'direct_diversity': args.direct_diversity,
                'specification_sha256': digest(spec_bytes), 'data_sha256': digest(data.read_bytes()),
                'reference_sha256': digest(reference.read_bytes()), 'representation_cache_sha256': cache_hash,
                'gemini_model': model,
                'python': platform.python_version(),
                'versions': {name: version(name) for name in ('numpy', 'scipy', 'scikit-learn', 'python-dotenv')},
                'code_sha256': {str(path.relative_to(ROOT)): digest(path.read_bytes()) for path in paths}}
    manifest_path = args.output / 'manifest.json'
    if args.resume:
        if json.loads(manifest_path.read_text()) != manifest:
            raise ValueError('Cannot resume with changed inputs or implementation')
    else:
        args.output.mkdir(parents=True, exist_ok=False)
        write_json(manifest_path, manifest)
    advisor = None
    if 'gemini_repair' in args.methods:
        advisor = lambda kind, menu: traced_repair_advice(lambda warning, options: request_repair(key, model, warning, options),
                                                   kind, menu)
    for seed in args.seeds:
        seed_dir = args.output / f'seed_{seed:02d}'
        seed_dir.mkdir(exist_ok=True)
        for method in args.methods:
            path = seed_dir / method
            status_path = path / 'status.json'
            if status_path.exists():
                saved = json.loads(status_path.read_text())
                if saved['status'] == 'completed':
                    blob = (path / 'run.jsonl.gz').read_bytes()
                    if (digest(blob) != saved['gzip_sha256']
                            or digest(gzip.decompress(blob)) != saved['uncompressed_sha256']):
                        raise ValueError('Completed run fingerprint mismatch')
                continue
            if path.exists():
                write_json(status_path, {'status': 'interrupted'})
                print(json.dumps({'seed': seed, 'method': method, 'status': 'interrupted'}), flush=True)
                continue
            started = time.perf_counter()
            try:
                run_one(path, seed, method, spec, advisor=advisor, model=model, dataset=args.dataset,
                        initial_pool=args.initial_pool, targeted_disagreement=args.targeted_disagreement,
                        direct_diversity=args.direct_diversity)
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
    if any(json.loads((args.output / f'seed_{seed:02d}' / method / 'status.json').read_text())['status'] != 'completed'
           for seed in args.seeds for method in args.methods):
        raise SystemExit('Some runs failed or were interrupted; inspect their status files')


if __name__ == '__main__':
    main()
