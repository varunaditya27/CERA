"""Generate residue-mean representations from a pinned ESM-2 model."""
import hashlib

import numpy as np
import torch

MODEL = 'facebook/esm2_t6_8M_UR50D'
REVISION = 'c731040fcd8d73dceaa04b0a8e6329b345b0f5df'
ALPHABET = set('ACDEFGHIKLMNPQRSTVWY')
FEATURES = 320


def sequence_id(sequence):
    if not isinstance(sequence, str) or not sequence or set(sequence) - ALPHABET:
        raise ValueError('Sequence must contain standard amino-acid letters')
    return hashlib.sha256(sequence.encode('ascii')).hexdigest()


def represent(sequences, tokenizer, model, device, batch_size=16):
    if not sequences or not isinstance(batch_size, int) or isinstance(batch_size, bool) or batch_size < 1:
        raise ValueError('Provide sequences and a positive batch size')
    items = list(sequences.items())
    for identifier, sequence in items:
        if sequence_id(sequence) != identifier:
            raise ValueError('Sequence identifier does not match sequence')
        if len(sequence) + 2 > model.config.max_position_embeddings:
            raise ValueError('Sequence exceeds model input limit')
    model.to(device=device, dtype=torch.float32).eval()
    result = []
    for offset in range(0, len(items), batch_size):
        batch = items[offset:offset + batch_size]
        inputs = tokenizer([sequence for _, sequence in batch], padding=True,
                           return_tensors='pt', return_special_tokens_mask=True, truncation=False)
        special = inputs.pop('special_tokens_mask').to(device)
        inputs = {key: value.to(device) for key, value in inputs.items()}
        mask = inputs['attention_mask'].bool() & ~special.bool()
        if mask.sum(dim=1).tolist() != [len(sequence) for _, sequence in batch]:
            raise ValueError('Tokenizer did not preserve every residue')
        with torch.inference_mode():
            hidden = model(**inputs).last_hidden_state
            if hidden.shape != (*mask.shape, FEATURES):
                raise ValueError('Unexpected model output shape')
            means = (hidden * mask.unsqueeze(-1)).sum(dim=1) / mask.sum(dim=1, keepdim=True)
        array = means.cpu().numpy()
        if not np.isfinite(array).all():
            raise ValueError('Non-finite representation')
        result.append(array)
    return np.concatenate(result, axis=0)
