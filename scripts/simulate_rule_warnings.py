#!/usr/bin/env python3
"""Record hand-labeled warning boundary cases, not biological outcomes."""
import argparse
import hashlib
import json
from pathlib import Path

from app.provenance.sources import source_hashes
from app.rewards.warning_checks import constraint_warning, diversity_warning

CANDIDATES = {'unchanged': 'AAAAA', 'one': 'CAAAA', 'four': 'CCCCA', 'five': 'CCCCC'}
CONSTRAINT = [
    ('one mutation', ['one'], 2, 2, False), ('four at limit', ['four'], 2, 2, False),
    ('five mutations', ['five'], 2, 2, True), ('two at limit', ['unchanged', 'one'], 2, 2, False),
    ('duplicate', ['one', 'one'], 2, 2, True), ('unknown', ['unknown'], 2, 2, True),
    ('budget', ['unchanged', 'one'], 1, 2, True), ('batch', ['unchanged', 'one'], 2, 1, True),
    ('empty', [], 2, 2, True), ('mixed', ['one', 'five'], 2, 2, True),
]
DIVERSITY = [
    ('one difference', {'a': 'AAAA', 'b': 'AAAC'}, True),
    ('two differences', {'a': 'AAAA', 'b': 'AACC'}, False),
    ('three differences', {'a': 'AAAA', 'b': 'ACCC'}, False),
    ('three variants', {'a': 'AAAA', 'b': 'AAAC', 'c': 'AACC'}, True),
    ('one variant', {'a': 'AAAA'}, None),
]


def summarize(cases):
    tp = sum(c['label'] is True and c['status'] == 'triggered' for c in cases)
    fn = sum(c['label'] is True and c['status'] == 'not_triggered' for c in cases)
    fp = sum(c['label'] is False and c['status'] == 'triggered' for c in cases)
    tn = sum(c['label'] is False and c['status'] == 'not_triggered' for c in cases)
    return {'true_positive': tp, 'false_negative': fn, 'false_positive': fp, 'true_negative': tn,
            'unavailable': sum(c['status'] == 'unavailable' for c in cases),
            'precision': tp / (tp + fp) if tp + fp else None,
            'recall': tp / (tp + fn) if tp + fn else None,
            'f1': 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else None,
            'false_alarm_rate': fp / (fp + tn) if fp + tn else None}


def simulate():
    constraints = []
    for name, ids, remaining, limit, label in CONSTRAINT:
        result = constraint_warning(ids, CANDIDATES, 'AAAAA', remaining, batch_size=limit)
        constraints.append({'name': name, 'ids': ids, 'remaining': remaining, 'limit': limit,
                            'label': label, 'status': result['status'], 'reason': result['reason']})
    diversity = []
    for name, batch, label in DIVERSITY:
        result = diversity_warning(batch)
        diversity.append({'name': name, 'batch': batch, 'label': label,
                          'status': result['status'], 'value': result['value']})
    return {'constraint': {'cases': constraints, 'summary': summarize(constraints)},
            'diversity': {'cases': diversity, 'summary': summarize(diversity)}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    report = {'scope': 'hand-labeled rule checks; not biological validation',
              'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'warning_source_sha256': source_hashes(('warning_checks.py',)), **simulate()}
    with args.output.open('x', encoding='utf-8') as file:
        json.dump(report, file, indent=2, allow_nan=False)
        file.write('\n')


if __name__ == '__main__':
    main()
