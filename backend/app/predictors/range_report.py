"""Reconstruct range coverage from recorded pre-reveal predictions."""
import csv
import json
from pathlib import Path

from app.predictors.prediction_intervals import batch_coverage


def summarize_ranges(log_path, output_path):
    events = [json.loads(line) for line in Path(log_path).read_text(encoding='utf-8').splitlines()]
    if not events or events[0]['event'] != 'start':
        raise ValueError('Missing run start')
    budget = events[0]['budget']
    pending = None
    covered_total = count_total = 0
    width_total = 0.0
    rows = []
    for event in events[1:]:
        if event['event'] == 'selection':
            if pending is not None or 'prediction_ranges' not in event:
                raise ValueError('Invalid pre-reveal selection record')
            pending = event
        elif event['event'] == 'reveal':
            if pending is None or pending['ids'] != list(event['measurements']):
                raise ValueError('Reveal does not match recorded selection')
            covered, count, width = batch_coverage(pending['prediction_ranges'], event['measurements'])
            covered_total += covered
            count_total += count
            width_total += width
            if event['remaining'] != budget - count_total:
                raise ValueError('Recorded budget does not match revealed measurements')
            rows.append((len(rows) + 1, count_total, covered, count, covered / count, width / count,
                         covered_total, count_total, covered_total / count_total, width_total / count_total))
            pending = None
    if pending is not None:
        raise ValueError('Incomplete run record')
    with Path(output_path).open('x', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['batch', 'new_measurements', 'batch_covered', 'batch_count', 'batch_coverage',
                         'batch_mean_width', 'cumulative_covered', 'cumulative_count',
                         'cumulative_coverage', 'cumulative_mean_width'])
        writer.writerows(rows)
    return rows
