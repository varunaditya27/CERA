"""Load eligible amylase variants and their original measurements."""
import csv
import hashlib
import io
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'data/raw/flip2/amylase/close_to_far.csv'
REFERENCE = ROOT / 'data/amylase_reference.fasta'


def load_amylase(data_path, reference_path, max_mutations):
    data = Path(data_path).read_bytes()
    reference_data = Path(reference_path).read_bytes()
    lines = reference_data.decode('utf-8').splitlines()
    reference = ''.join(lines[1:]) if lines and lines[0].startswith('>') else ''
    alphabet = set('ACDEFGHIKLMNPQRSTVWY')
    if not reference or set(reference) - alphabet:
        raise ValueError('Invalid reference sequence')
    rows = csv.DictReader(io.StringIO(data.decode('utf-8'), newline=''))
    if not {'sequence', 'target', 'set', 'validation'}.issubset(rows.fieldnames or []):
        raise ValueError('Missing dataset columns')
    scores, sequences, train, seen = {}, {}, [], set()
    for row in rows:
        sequence = row['sequence']
        if not sequence or set(sequence) - alphabet or len(sequence) != len(reference) or sequence in seen:
            raise ValueError('Invalid or duplicate sequence')
        seen.add(sequence)
        score = float(row['target'])
        if not math.isfinite(score) or row['set'] not in ('train', 'test') or row['validation'] not in ('True', 'False'):
            raise ValueError('Invalid dataset row')
        if sum(a != b for a, b in zip(sequence, reference)) > max_mutations:
            continue
        identifier = hashlib.sha256(sequence.encode('ascii')).hexdigest()
        sequences[identifier] = sequence
        scores[identifier] = score
        if row['set'] == 'train':
            train.append(identifier)
    return sequences, scores, train, hashlib.sha256(data).hexdigest(), hashlib.sha256(reference_data).hexdigest()
