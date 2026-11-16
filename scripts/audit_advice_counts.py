#!/usr/bin/env python3
"""Check recorded model-advice accounting against repeated-run summaries."""
import argparse
import collections
import csv
import gzip
import hashlib
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    args = parser.parse_args()
    with (args.root / 'summary.csv').open(newline='', encoding='utf-8') as file:
        rows = list(csv.DictReader(file))
    totals = collections.Counter()
    token_types = collections.Counter()
    for row in rows:
        if row['status'] != 'completed':
            continue
        path = args.root / f"seed_{int(row['seed']):02d}" / row['method'] / 'run.jsonl.gz'
        advice = []
        with gzip.open(path, 'rt', encoding='utf-8') as file:
            for line in file:
                event = json.loads(line)
                if event['event'] == 'method':
                    advice.extend(action['advice'] for action in event['settings'].get('repair_actions', [])
                                  if action.get('advice'))
        attempts = [attempt for item in advice for attempt in item['attempts']]
        expected = {'advice_gemini': sum(item['source'] == 'gemini' for item in advice),
                    'advice_fallback': sum(item['source'] == 'fallback' for item in advice),
                    'advice_request_attempts': sum(item['status'] != 'invalid_configuration' for item in attempts),
                    'advice_reported_tokens': sum(item.get('usage', {}).get('totalTokenCount', 0) for item in attempts)}
        if any(int(row[key]) != value for key, value in expected.items()):
            raise ValueError(f'Advice accounting mismatch for seed {row["seed"]}, method {row["method"]}')
        totals.update(expected)
        for attempt in attempts:
            token_types.update(attempt.get('usage', {}))
    result = {'runs_checked': len(rows), 'totals': dict(totals), 'reported_token_types': dict(token_types),
              'audit_script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    with (args.root / 'advice_audit.json').open('x', encoding='utf-8') as file:
        json.dump(result, file, indent=2)
        file.write('\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
