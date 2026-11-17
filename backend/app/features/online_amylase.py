"""Generate Amylase representations with the locally verified cache model."""
import csv
import hashlib
import json
import threading
from functools import lru_cache
from pathlib import Path

import numpy as np

from app.datasets.amylase import DATA
from app.features.amylase_representations import CACHE, CACHE_SHA256, load_verified_representations
from app.features.representations import MODEL, REVISION, represent, sequence_id

_lock = threading.Lock()


@lru_cache(maxsize=1)
def _encoder():
    import torch
    import transformers
    from huggingface_hub import hf_hub_download
    from transformers import AutoModel, AutoTokenizer

    if hashlib.sha256(CACHE.read_bytes()).hexdigest() != CACHE_SHA256:
        raise ValueError('Representation cache fingerprint mismatch')
    with np.load(CACHE, allow_pickle=False) as archive:
        settings = json.loads(archive['metadata'].item())['settings']
    if (settings['model'] != MODEL or settings['revision'] != REVISION
            or settings['torch'] != torch.__version__ or settings['transformers'] != transformers.__version__
            or settings['code_sha256']['backend/app/representations.py'] != hashlib.sha256(Path(__file__).with_name('representations.py').read_bytes()).hexdigest()):
        raise ValueError('Representation settings do not match cache')
    for name, expected in settings['model_files_sha256'].items():
        path = hf_hub_download(MODEL, name, revision=REVISION, local_files_only=True)
        if hashlib.sha256(Path(path).read_bytes()).hexdigest() != expected:
            raise ValueError('Representation model file fingerprint mismatch')
    tokenizer = AutoTokenizer.from_pretrained(MODEL, revision=REVISION, local_files_only=True)
    model = AutoModel.from_pretrained(MODEL, revision=REVISION, local_files_only=True, add_pooling_layer=False)
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    vectors = load_verified_representations()
    with DATA.open(newline='', encoding='utf-8') as file:
        rows = list(csv.DictReader(file))
    examples = [rows[index]['sequence'] for index in (0, 100, 1000)]
    calculated = represent({sequence_id(s): s for s in examples}, tokenizer, model, device, batch_size=1)
    expected = np.asarray([vectors[sequence_id(s)] for s in examples])
    if not np.allclose(calculated, expected, rtol=1e-5, atol=1e-5):
        raise ValueError('Representation check differs from cache')
    return tokenizer, model, device


def represent_new(sequence):
    with _lock:
        tokenizer, model, device = _encoder()
        return represent({sequence_id(sequence): sequence}, tokenizer, model, device, batch_size=1)[0]
