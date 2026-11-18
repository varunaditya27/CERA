"""Read the pinned, audited Amylase comparison for the web workspace."""
import hashlib
import json
from pathlib import Path

from fastapi import APIRouter, HTTPException

router = APIRouter()
AUDIT = Path(__file__).resolve().parents[3] / 'output/hybrid/mixed_search_comparison_191_200_audit.json'
AUDIT_SHA256 = '6eb00a0f5b31b7bac775398ed98b2175116651c402b71989bc3947e3fa97e975'


@router.get('/api/results/mixed-search')
def mixed_search_results():
    try:
        raw = AUDIT.read_bytes()
        if hashlib.sha256(raw).hexdigest() != AUDIT_SHA256:
            raise ValueError('Audit fingerprint mismatch')
        data = json.loads(raw)
        runs = data['runs']
        return {
            'pairs': len(runs),
            'mixed_higher': data['mixed_higher'], 'ties': data['ties'], 'ridge_higher': data['ridge_higher'],
            'methods': {method: {
                'covered': sum(run[method]['covered'] for run in runs),
                'measured': sum(run[method]['range_count'] for run in runs),
                'mean_width': sum(run[method]['mean_range_width'] for run in runs) / len(runs),
                'mean_seconds': sum(run[method]['elapsed_seconds'] for run in runs) / len(runs),
            } for method in ('mixed', 'ridge')},
            'audit_sha256': AUDIT_SHA256,
        }
    except (OSError, ValueError, KeyError, TypeError, ZeroDivisionError) as error:
        raise HTTPException(status_code=503, detail='Audited results unavailable') from error
