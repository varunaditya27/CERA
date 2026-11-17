"""Run the independent local selection and repair replay checks."""
import json

from app.datasets.registry import dataset_source
from app.workspace import runs_service
from app.workspace.run_review import review_run


def audit_run(run_id):
    from app.analysis.selection_audit import audit_decisions

    review = review_run(run_id)
    dataset = review['summary'].get('dataset', 'amylase')
    data, reference, loader = dataset_source(dataset)
    events = [json.loads(line) for line in (runs_service.RUNS / run_id / 'run.jsonl').read_text(encoding='utf-8').splitlines()]
    sequences, scores, train, _, _ = loader(data, reference, events[0]['max_mutations'])
    if dataset == 'amylase':
        from app.features import amylase_representations
        vectors, cache_hash = amylase_representations.load_verified_representations(), amylase_representations.CACHE_SHA256
    elif dataset == 'ired':
        from app.features import ired_representations
        vectors, cache_hash = ired_representations.load_verified_representations(), ired_representations.CACHE_SHA256
    else:
        from app.features import hydro_representations
        protein = dataset.removeprefix('hydro-')
        vectors, cache_hash = hydro_representations.load_verified_representations(protein), hydro_representations.CACHE_HASHES[protein]
    return {'id': run_id, **audit_decisions(events, sequences, scores, train, vectors, cache_hash)}
