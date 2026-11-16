#!/usr/bin/env python3
"""Verify ESM pooling or build a score-free FLIP2 representation cache."""
import argparse
import csv
import hashlib
import importlib.metadata
import io
import json
import os
import time
from pathlib import Path

import numpy as np
import torch
import transformers
from huggingface_hub import hf_hub_download
from transformers import AutoModel, AutoTokenizer

from app import amylase, ired
from app.representation_cache import load_cache, save_cache
from app.representations import MODEL, REVISION, represent, sequence_id


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='New cache path; required unless verifying')
    parser.add_argument('--dataset', choices=('amylase', 'ired'), default='amylase')
    parser.add_argument('--verify-only', action='store_true', help='Check the real model without writing a cache')
    parser.add_argument('--device', choices=('cpu', 'cuda'), default='cpu')
    parser.add_argument('--batch-size', type=int, default=16)
    args = parser.parse_args()
    dataset = {'amylase': amylase, 'ired': ired}[args.dataset]
    if args.verify_only == (args.output is not None):
        parser.error('Choose --verify-only or --output')
    if args.output is not None and args.output.exists():
        raise FileExistsError(args.output)
    if args.device == 'cuda' and not torch.cuda.is_available():
        raise RuntimeError('CUDA was requested but is unavailable')

    tokenizer = AutoTokenizer.from_pretrained(MODEL, revision=REVISION)
    model = AutoModel.from_pretrained(MODEL, revision=REVISION, add_pooling_layer=False)
    ref_data = dataset.REFERENCE.read_bytes()
    reference = ''.join(ref_data.decode('utf-8').splitlines()[1:])
    if args.verify_only:
        short = reference[:57]
        alone = represent({sequence_id(reference): reference}, tokenizer, model, args.device, 1)
        batch = represent({sequence_id(reference): reference, sequence_id(short): short},
                          tokenizer, model, args.device, 2)
        difference = float(np.max(np.abs(alone[0] - batch[0])))
        if not np.allclose(alone[0], batch[0], rtol=1e-5, atol=1e-5):
            raise ValueError('Padded and unpadded representations differ')
        print(json.dumps({'shape': list(batch.shape), 'finite': bool(np.isfinite(batch).all()),
                          'padding_max_difference': difference, 'device': args.device}))
        return

    data = dataset.DATA.read_bytes()
    rows = csv.DictReader(io.StringIO(data.decode('utf-8'), newline=''))
    if 'sequence' not in (rows.fieldnames or []):
        raise ValueError('Missing sequence column')
    sequences = {}
    for row in rows:
        sequence = row['sequence']
        identifier = sequence_id(sequence)
        if identifier in sequences:
            raise ValueError('Duplicate sequence identifier')
        sequences[identifier] = sequence
    if not sequences:
        raise ValueError('Dataset contains no sequences')
    file_hashes = {}
    for name in ('config.json', 'model.safetensors', 'special_tokens_map.json',
                 'tokenizer_config.json', 'vocab.txt'):
        path = hf_hub_download(MODEL, name, revision=REVISION, local_files_only=True)
        file_hashes[name] = hashlib.sha256(Path(path).read_bytes()).hexdigest()
    settings = {'dataset_sha256': hashlib.sha256(data).hexdigest(),
                'reference_sha256': hashlib.sha256(ref_data).hexdigest(),
                'model': MODEL, 'revision': REVISION, 'model_files_sha256': file_hashes,
                'pooling': 'residue_mean_excluding_padding_and_special_tokens',
                'dtype': 'float32', 'device': args.device, 'batch_size': args.batch_size,
                'torch': torch.__version__, 'transformers': transformers.__version__, 'numpy': np.__version__,
                'huggingface_hub': importlib.metadata.version('huggingface-hub'),
                'tokenizers': importlib.metadata.version('tokenizers'),
                'safetensors': importlib.metadata.version('safetensors'),
                'code_sha256': {str(path.relative_to(Path(__file__).resolve().parents[1])): hashlib.sha256(path.read_bytes()).hexdigest()
                                for path in (Path(__file__).resolve(),
                                             Path(__file__).resolve().parents[1] / 'backend/app/representations.py',
                                             Path(__file__).resolve().parents[1] / 'backend/app/representation_cache.py')},
                'cuda_build': torch.version.cuda, 'native_jit_disabled': os.getenv('TORCH_DISABLE_NATIVE_JIT') == '1',
                'gpu': torch.cuda.get_device_name() if args.device == 'cuda' else None}
    if args.device == 'cuda':
        torch.cuda.reset_peak_memory_stats()
        torch.cuda.synchronize()
    start = time.perf_counter()
    vectors = represent(sequences, tokenizer, model, args.device, args.batch_size)
    if args.device == 'cuda':
        torch.cuda.synchronize()
    observations = {'sequence_count': len(sequences), 'embedding_seconds': time.perf_counter() - start,
                    'peak_allocated_mib': torch.cuda.max_memory_allocated() / 1048576 if args.device == 'cuda' else None}
    save_cache(args.output, list(sequences), vectors, settings, observations)
    load_cache(args.output, list(sequences), settings)
    print(json.dumps({'output': str(args.output), **observations}))


if __name__ == '__main__':
    main()
