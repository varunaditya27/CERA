"""Compare recorded warnings with later, separately observed range coverage."""
import math


KINDS = ('support_shift', 'coverage')


def evaluate(source_events, replay_events):
    batches, pending = [], None
    for event in source_events:
        if event['event'] == 'selection':
            if pending is not None:
                raise ValueError('Selection before prior reveal')
            ids = event['ids']
            if not ids or len(ids) != len(set(ids)):
                raise ValueError('Invalid selection identifiers')
            pending = (ids, event['prediction_ranges'])
        elif event['event'] == 'reveal':
            if pending is None:
                raise ValueError('Reveal without selection')
            ids, ranges = pending
            values = event['measurements']
            if list(values) != ids:
                raise ValueError('Selection and reveal identifiers differ')
            covered = []
            for identifier in ids:
                lower, upper = ranges[identifier]['lower'], ranges[identifier]['upper']
                score = values[identifier]
                if not all(math.isfinite(x) for x in (lower, upper, score)) or lower > upper:
                    raise ValueError('Invalid range or measurement')
                covered.append(lower <= score <= upper)
            batches.append((ids, covered))
            pending = None
    if pending is not None or not batches:
        raise ValueError('Incomplete source record')
    all_ids = [identifier for ids, _ in batches for identifier in ids]
    if len(all_ids) != len(set(all_ids)):
        raise ValueError('Repeated measurement')
    warnings = {}
    references = {}
    current_round = 0
    for event in replay_events:
        if event['event'] == 'reveal_reference':
            round_number = event['round']
            if round_number != current_round + 1:
                raise ValueError('Replay reveals out of order')
            current_round = round_number
            references[round_number] = event['identifiers']
        elif event['event'] == 'warning' and event['type'] in KINDS:
            key = (event['round'], event['type'])
            if key in warnings or event['stage'] != 'post_reveal' or event['status'] not in (
                    'triggered', 'not_triggered', 'unavailable') or event['round'] != current_round:
                raise ValueError('Invalid replay warning')
            warnings[key] = event['status']
    if references != {i + 1: batch[0] for i, batch in enumerate(batches)}:
        raise ValueError('Replay and source selections differ')
    if set(warnings) != {(i + 1, kind) for i in range(len(batches)) for kind in KINDS}:
        raise ValueError('Missing or extra replay warnings')
    rows = []
    for index in range(len(batches)):
        later = [value for _, covered in batches[index + 1:] for value in covered][:30]
        for kind in KINDS:
            rows.append({'round': index + 1, 'warning': kind, 'status': warnings[(index + 1, kind)],
                         'later_count': len(later), 'later_covered': sum(later) if len(later) == 30 else None,
                         'later_low_coverage': sum(later) < 26 if len(later) == 30 else None})
    return rows


def summarize(rows):
    counts = {key: 0 for key in ('true_alarm', 'false_alarm', 'miss', 'true_negative',
                                  'warning_unavailable', 'followup_unavailable')}
    for row in rows:
        if row['status'] == 'unavailable':
            counts['warning_unavailable'] += 1
        elif row['later_low_coverage'] is None:
            counts['followup_unavailable'] += 1
        else:
            alarm, outcome = row['status'] == 'triggered', row['later_low_coverage']
            key = ('true_alarm' if outcome else 'false_alarm') if alarm else ('miss' if outcome else 'true_negative')
            counts[key] += 1
    positive = counts['true_alarm'] + counts['false_alarm']
    events = counts['true_alarm'] + counts['miss']
    return {**counts, 'precision': counts['true_alarm'] / positive if positive else None,
            'recall': counts['true_alarm'] / events if events else None}
