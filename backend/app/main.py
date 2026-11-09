"""Read-only API for the CERA research workspace."""
import csv
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parents[2]
app = FastAPI(title='CERA API', version='0.1.0', description='Dataset catalog and future experiment integration boundary.')
app.add_middleware(CORSMiddleware, allow_origins=['http://localhost:3000', 'http://127.0.0.1:3000'], allow_methods=['GET'], allow_headers=['*'])

class Dataset(BaseModel):
    id: str
    name: str
    source: str
    purpose: str
    shift: str
    split: str
    note: str
    variants: int | None
    available: bool

CATALOG = [
    ('amylase', 'Alpha amylase', 'FLIP2', 'Development', 'Position', 'Close to far', 'Mutations move away from the active site.', 'data/raw/flip2/amylase/close_to_far.csv'),
    ('ired', 'Imine reductase', 'FLIP2', 'Evaluation', 'Mutation count', 'Two to many', 'Generalization to variants with more mutations.', 'data/raw/flip2/ired/two_to_many.csv'),
    ('hydro', 'Hydrophobic core', 'FLIP2', 'Evaluation', 'Fitness', 'Low to high', 'Three protein backbones require separate handling.', 'data/raw/flip2/hydro/low_to_high.csv'),
    ('gb1', 'GB1', 'FLIP', 'Additional', 'Fitness', 'Low vs high', 'A four-site protein binding landscape.', 'data/raw/flip/gb1/low_vs_high.csv'),
    ('gfp', 'Green fluorescent protein', 'ProteinGym', 'Additional', 'Not assigned', 'Needs seed split', 'Fluorescence assay with multi-mutant variants.', 'data/raw/proteingym/GFP_AEQVI_Sarkisyan_2016.csv'),
]

@app.get('/api/health')
def health():
    return {'status': 'ok'}

@app.get('/api/datasets', response_model=list[Dataset])
def datasets():
    result = []
    for identifier, name, source, purpose, shift, split, note, relative in CATALOG:
        path = ROOT / relative
        count = None
        if path.is_file():
            with path.open(newline='', encoding='utf-8') as file:
                count = sum(1 for _ in csv.reader(file)) - 1
        result.append(Dataset(id=identifier, name=name, source=source, purpose=purpose, shift=shift, split=split, note=note, variants=count, available=count is not None))
    return result
