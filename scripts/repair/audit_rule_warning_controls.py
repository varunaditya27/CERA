#!/usr/bin/env python3
"""Recheck saved warning cases without invoking warning functions."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path

from app.provenance.sources import source_hashes


def audit(report):
    script = Path(__file__).with_name('simulate_rule_warnings.py')
    if (report['script_sha256'] != hashlib.sha256(script.read_bytes()).hexdigest()
            or report['warning_source_sha256'] != source_hashes(('warning_checks.py',))):
        raise ValueError('Source fingerprint mismatch')
    candidates = {'unchanged': 'AAAAA', 'one': 'CAAAA', 'four': 'CCCCA', 'five': 'CCCCC'}
    fixtures = [
        ('one mutation', ['one'], 2, 2, False), ('four at limit', ['four'], 2, 2, False),
        ('five mutations', ['five'], 2, 2, True), ('two at limit', ['unchanged', 'one'], 2, 2, False),
        ('duplicate', ['one', 'one'], 2, 2, True), ('unknown', ['unknown'], 2, 2, True),
        ('budget', ['unchanged', 'one'], 1, 2, True), ('batch', ['unchanged', 'one'], 2, 1, True),
        ('empty', [], 2, 2, True), ('mixed', ['one', 'five'], 2, 2, True),
    ]
    diversity = [
        ('one difference', {'a': 'AAAA', 'b': 'AAAC'}, True),
        ('two differences', {'a': 'AAAA', 'b': 'AACC'}, False),
        ('three differences', {'a': 'AAAA', 'b': 'ACCC'}, False),
        ('three variants', {'a': 'AAAA', 'b': 'AAAC', 'c': 'AACC'}, True),
        ('one variant', {'a': 'AAAA'}, None),
    ]
    cases = report['constraint']['cases']
    if len(cases) != len(fixtures):
        raise ValueError('Constraint count mismatch')
    for case, (name, ids, remaining, limit, label) in zip(cases, fixtures):
        reasons = []
        if not ids: reasons.append('empty_batch')
        if len(ids) != len(set(ids)): reasons.append('duplicate')
        if len(ids) > remaining or len(ids) > limit: reasons.append('budget_or_batch_limit')
        for identifier in ids:
            if identifier not in candidates: reasons.append('unknown_or_already_revealed')
            elif sum(a != b for a, b in zip(candidates[identifier], 'AAAAA')) > 4: reasons.append('mutation_limit')
        expected = {'name': name, 'ids': ids, 'remaining': remaining, 'limit': limit, 'label': label,
                    'status': 'triggered' if reasons else 'not_triggered',
                    'reason': ','.join(sorted(set(reasons))) if reasons else None}
        if case != expected or bool(reasons) != label:
            raise ValueError('Constraint case mismatch')
    cases = report['diversity']['cases']
    if len(cases) != len(diversity):
        raise ValueError('Diversity count mismatch')
    for case, (name, batch, label) in zip(cases, diversity):
        distances = [sum(a != b for a, b in zip(left, right))
                     for left, right in itertools.combinations(batch.values(), 2)]
        value = sum(distances) / len(distances) if distances else None
        status = 'unavailable' if value is None else ('triggered' if value < 2 else 'not_triggered')
        if (case != {'name': name, 'batch': batch, 'label': label, 'status': status, 'value': value}
                or (None if value is None else value < 2) != label):
            raise ValueError('Diversity case mismatch')
    for kind in ('constraint', 'diversity'):
        cases = report[kind]['cases']
        tp = sum(c['label'] is True and c['status'] == 'triggered' for c in cases)
        fn = sum(c['label'] is True and c['status'] == 'not_triggered' for c in cases)
        fp = sum(c['label'] is False and c['status'] == 'triggered' for c in cases)
        tn = sum(c['label'] is False and c['status'] == 'not_triggered' for c in cases)
        expected = {'true_positive': tp, 'false_negative': fn, 'false_positive': fp, 'true_negative': tn,
                    'unavailable': sum(c['status'] == 'unavailable' for c in cases),
                    'precision': tp / (tp + fp) if tp + fp else None,
                    'recall': tp / (tp + fn) if tp + fn else None,
                    'f1': 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else None,
                    'false_alarm_rate': fp / (fp + tn) if fp + tn else None}
        if report[kind]['summary'] != expected:
            raise ValueError('Summary mismatch')
    return {'constraint_cases': len(fixtures), 'diversity_cases': len(diversity)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report', type=Path)
    args = parser.parse_args()
    print(json.dumps(audit(json.loads(args.report.read_text())), sort_keys=True))


if __name__ == '__main__':
    main()
