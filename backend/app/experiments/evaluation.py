"""Evaluate completed finite-pool run records after selection has finished."""
import math


def evaluate(events, scores, train_ids, data_hash, reference_hash):
    if not events or events[0].get('event') != 'start' or not scores:
        raise ValueError('Missing run start or source scores')
    start = events[0]
    if start['data_sha256'] != data_hash or start['reference_sha256'] != reference_hash:
        raise ValueError('Run source fingerprint mismatch')
    known = dict(start['initial'])
    if (len(known) != start['initial_count'] or not set(known).issubset(train_ids)
            or any(i not in scores or scores[i] != value for i, value in known.items())):
        raise ValueError('Initial observations mismatch')
    values = sorted(scores.values(), reverse=True)
    optimum, top_threshold = values[0], values[math.ceil(len(values) * 0.01) - 1]
    budget = start['budget']
    pending = None
    stop = start['stop_reason']
    covered = measured_with_ranges = 0
    width_sum = 0.0
    rows = []

    def snapshot(count):
        best = max(known.values())
        rows.append({'new_measurements': count, 'best_observed': best, 'pool_regret': optimum - best,
                     'found_top_one_percent': best >= top_threshold})

    snapshot(0)
    for event in events[1:]:
        if event['event'] == 'selection':
            ids = event['ids']
            if (stop is not None or pending is not None or not ids or len(ids) > start['batch_size']
                    or len(set(ids)) != len(ids) or any(i not in scores or i in known for i in ids)
                    or len(ids) > budget - (len(known) - start['initial_count'])):
                raise ValueError('Invalid selection chronology or identifiers')
            pending = event
        elif event['event'] == 'reveal':
            measurements = event['measurements']
            if (stop is not None or pending is None or pending['ids'] != list(measurements)
                    or any(scores[i] != value for i, value in measurements.items())):
                raise ValueError('Invalid reveal')
            ranges = pending.get('prediction_ranges')
            if ranges is not None:
                if not set(measurements).issubset(ranges):
                    raise ValueError('Missing pre-reveal ranges')
                for identifier, value in measurements.items():
                    lower, upper = ranges[identifier]['lower'], ranges[identifier]['upper']
                    if not math.isfinite(lower) or not math.isfinite(upper) or lower > upper:
                        raise ValueError('Invalid pre-reveal range')
                    covered += lower <= value <= upper
                    width_sum += upper - lower
                    measured_with_ranges += 1
            known.update(measurements)
            count = len(known) - start['initial_count']
            if event['remaining'] != budget - count:
                raise ValueError('Incorrect remaining budget')
            expected = ('budget_exhausted' if count == budget else
                        'no_candidates' if len(known) == len(scores) else None)
            if event['stop_reason'] != expected:
                raise ValueError('Incorrect natural stop')
            stop = expected
            snapshot(count)
            pending = None
        elif event['event'] == 'stop':
            if (stop is not None or pending is not None or event['stop_reason'] not in ('failed_repairs', 'no_neighbors')
                    or event['remaining'] != budget - (len(known) - start['initial_count'])):
                raise ValueError('Invalid early stop')
            stop = event['stop_reason']
    if pending is not None or stop is None:
        raise ValueError('Incomplete run')
    return {'curve': rows, 'stop_reason': stop, 'pool_optimum': optimum, 'top_threshold': top_threshold,
            'covered': covered if measured_with_ranges else None, 'range_count': measured_with_ranges,
            'mean_range_width': width_sum / measured_with_ranges if measured_with_ranges else None}
