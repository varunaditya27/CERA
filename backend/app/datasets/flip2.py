"""Validate FLIP2 rows and expose one eligible sequence group to a runner."""
import csv
import hashlib
import io
import math
from pathlib import Path


def load_flip2(data_path, reference_path, max_mutations, group_lengths=None):
    if not isinstance(max_mutations, int) or isinstance(max_mutations, bool) or max_mutations < 0:
        raise ValueError('Invalid mutation limit')
    data, reference_data = Path(data_path).read_bytes(), Path(reference_path).read_bytes()
    lines = reference_data.decode('utf-8').splitlines()
    reference = ''.join(lines[1:]) if lines and lines[0].startswith('>') else ''
    alphabet = set('ACDEFGHIKLMNPQRSTVWY')
    if not reference or set(reference) - alphabet or (group_lengths is not None and len(reference) not in group_lengths):
        raise ValueError('Invalid reference sequence')
    rows = csv.DictReader(io.StringIO(data.decode('utf-8'), newline=''))
    if not {'sequence', 'target', 'set', 'validation'}.issubset(rows.fieldnames or []):
        raise ValueError('Missing dataset columns')
    scores, sequences, train, seen = {}, {}, [], set()
    for row in rows:
        sequence = row['sequence']
        valid_lengths = group_lengths if group_lengths is not None else {len(reference)}
        if not sequence or set(sequence) - alphabet or len(sequence) not in valid_lengths or sequence in seen:
            raise ValueError('Invalid or duplicate sequence')
        seen.add(sequence)
        score = float(row['target'])
        if not math.isfinite(score) or row['set'] not in ('train', 'test') or row['validation'] not in ('True', 'False'):
            raise ValueError('Invalid dataset row')
        if len(sequence) != len(reference) or sum(a != b for a, b in zip(sequence, reference)) > max_mutations:
            continue
        identifier = hashlib.sha256(sequence.encode('ascii')).hexdigest()
        sequences[identifier] = sequence
        scores[identifier] = score
        if row['set'] == 'train':
            train.append(identifier)
    if not sequences:
        raise ValueError('No eligible sequences for reference')
    return sequences, scores, train, hashlib.sha256(data).hexdigest(), hashlib.sha256(reference_data).hexdigest()
