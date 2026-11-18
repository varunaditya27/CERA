"""Predictions from the pinned Amylase development model and representation cache."""
import hashlib
from functools import lru_cache
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from app.datasets.amylase import DATA, REFERENCE, ROOT

router = APIRouter()
MODEL = ROOT / 'output/amylase/hybrid/amylase_hybrid_seed181_final.npz'
MODEL_SHA256 = '747968886935e3890fa0d4d9c95d1962a024cf35a4c55ac19672cd1e6a17e737'
ALPHABET = set('ACDEFGHIKLMNPQRSTVWY')


class PredictionRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    sequence: str = Field(min_length=1, max_length=1000)


@lru_cache(maxsize=1)
def prediction_resources():
    from app.predictors.hybrid_snapshot import load_hybrid_snapshot
    from app.features.amylase_representations import CACHE_SHA256, load_verified_representations

    model = load_hybrid_snapshot(MODEL, expected_sha256=MODEL_SHA256)
    context = model.metadata['context']
    if (context['data_sha256'] != hashlib.sha256(DATA.read_bytes()).hexdigest()
            or context['reference_sha256'] != hashlib.sha256(REFERENCE.read_bytes()).hexdigest()
            or context['cache_sha256'] != CACHE_SHA256):
        raise ValueError('Model and representation sources do not match')
    vectors = load_verified_representations()
    reference = ''.join(REFERENCE.read_text(encoding='utf-8').splitlines()[1:])
    return model, vectors, reference


@router.post('/api/predictions/amylase')
def predict_amylase(request: PredictionRequest):
    sequence = request.sequence.strip().upper()
    if not sequence or set(sequence) - ALPHABET:
        raise HTTPException(status_code=422, detail='Use standard amino-acid letters without spaces.')
    try:
        model, vectors, reference = prediction_resources()
    except (OSError, ValueError, ImportError) as error:
        raise HTTPException(status_code=503, detail='Development model or verified representations unavailable.') from error
    if len(sequence) != len(reference) or sum(a != b for a, b in zip(sequence, reference)) > 4:
        raise HTTPException(status_code=422, detail='Sequence must match the Amylase reference length and have at most four changes.')
    identifier = hashlib.sha256(sequence.encode('ascii')).hexdigest()
    if identifier in vectors:
        vector, representation_source = vectors[identifier], 'cache'
    else:
        try:
            from app.features.online_amylase import represent_new
            vector, representation_source = represent_new(sequence), 'generated'
        except (OSError, ValueError, ImportError, RuntimeError, KeyError) as error:
            raise HTTPException(status_code=503, detail='Local sequence representation model unavailable.') from error
    prediction = model.predict([vector])
    context = model.metadata['context']
    role = ('fitting' if identifier in context['fitting_ids'] else
            'range_setting' if identifier in context['reserved_ids'] else 'unobserved_in_episode')
    return {'mean': float(prediction['mean'][0]), 'lower': float(prediction['lower'][0]),
            'upper': float(prediction['upper'][0]), 'observed_role': role, 'representation_source': representation_source, 'model_sha256': MODEL_SHA256}
