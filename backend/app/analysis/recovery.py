"""Summarize later range coverage after the first recorded coverage warning."""
from collections import deque

from app.predictors.prediction_intervals import batch_coverage


def summarize_recovery(events):
    events = iter(events)
    start = next(events, None)
    if (not start or start.get('event') != 'start' or not isinstance(start.get('budget'), int)
            or start['budget'] < 0 or not isinstance(start.get('batch_size'), int) or start['batch_size'] < 1):
        raise ValueError('Invalid run start')
    budget = start['budget']
    seen = set(start['initial'])
    history = deque(maxlen=30)
    followup = deque(maxlen=30)
    selected = None
    needs_warning = False
    warning_after = None
    total = later = 0
    windows = []
    recovery = None
    stop = start['stop_reason']
    for event in events:
        kind = event['event']
        if kind == 'selection':
            ids = event['ids']
            if (selected is not None or needs_warning or stop is not None or not ids or len(ids) != len(set(ids))
                    or set(ids) & seen or len(ids) > min(start['batch_size'], budget - total)
                    or 'prediction_ranges' not in event):
                raise ValueError('Invalid selection chronology or identifiers')
            selected = event
        elif kind == 'reveal':
            if selected is None or needs_warning or stop is not None or selected['ids'] != list(event['measurements']):
                raise ValueError('Invalid reveal chronology')
            ranges, measurements = selected['prediction_ranges'], event['measurements']
            batch_coverage(ranges, measurements)
            for identifier, value in measurements.items():
                bounds = ranges[identifier]
                observation = (bounds['lower'] <= value <= bounds['upper'], bounds['upper'] - bounds['lower'])
                history.append(observation)
                if warning_after is not None:
                    followup.append(observation)
                    later += 1
            total += len(measurements)
            seen.update(measurements)
            if event['remaining'] != budget - total:
                raise ValueError('Incorrect remaining budget')
            stop = event['stop_reason']
            if (stop not in (None, 'budget_exhausted', 'no_candidates')
                    or (stop == 'budget_exhausted') != (total == budget)):
                raise ValueError('Incorrect natural stop')
            if warning_after is not None and len(followup) == 30:
                covered = sum(item[0] for item in followup)
                window = {'after_measurements': later, 'covered': covered, 'count': 30,
                          'coverage': covered / 30, 'mean_width': sum(item[1] for item in followup) / 30}
                windows.append(window)
                if recovery is None and 26 <= covered <= 28:
                    recovery = window.copy()
            selected = None
            needs_warning = True
        elif kind == 'warning' and event['type'] == 'coverage':
            if not needs_warning:
                raise ValueError('Coverage warning without preceding reveal')
            expected = ('unavailable' if len(history) < 30 else
                        'triggered' if sum(item[0] for item in history) < 22.5 else 'not_triggered')
            if event['status'] != expected:
                raise ValueError('Coverage warning does not match recorded measurements')
            if warning_after is None and expected == 'triggered':
                warning_after = total
            needs_warning = False
        elif kind == 'stop':
            if (selected is not None or needs_warning or stop is not None or event['remaining'] != budget - total
                    or event['stop_reason'] not in ('failed_repairs', 'no_neighbors')):
                raise ValueError('Invalid stop chronology')
            stop = event['stop_reason']
    if selected is not None or needs_warning or stop not in ('budget_exhausted', 'no_candidates', 'failed_repairs', 'no_neighbors'):
        raise ValueError('Incomplete run')
    status = ('no_warning' if warning_after is None else 'recovered' if recovery is not None else
              'insufficient_followup' if later < 30 else 'not_recovered')
    return {'status': status, 'warning_after_measurements': warning_after, 'followup_measurements': later,
            'recovery': recovery, 'windows': windows, 'stop_reason': stop, 'new_measurements': total}
