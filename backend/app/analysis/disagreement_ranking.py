"""Compare a saved disagreement warning with the selected batch's measured ordering."""
import math

from scipy.stats import spearmanr


def evaluate(source, replay):
    selections, reveals = [], []
    for event in source:
        if event['event'] == 'selection':
            if len(selections) != len(reveals):
                raise ValueError('Selection before prior reveal')
            selections.append(event)
        elif event['event'] == 'reveal':
            if len(selections) != len(reveals) + 1:
                raise ValueError('Unexpected reveal')
            reveals.append(event)
    if not selections or len(selections) != len(reveals):
        raise ValueError('Incomplete source')
    warnings, references, current = {}, {}, 0
    for event in replay:
        if event['event'] == 'warning' and event['type'] == 'disagreement':
            number = event['round']
            if (number != current + 1 or number in warnings or event['stage'] != 'pre_reveal'
                    or event['status'] not in ('triggered', 'not_triggered', 'unavailable')):
                raise ValueError('Invalid disagreement warning')
            warnings[number] = event
        elif event['event'] == 'reveal_reference':
            number = event['round']
            if number != current + 1 or number not in warnings:
                raise ValueError('Invalid replay reveal chronology')
            current = number
            references[number] = event['identifiers']
    if current != len(selections) or len(warnings) != current:
        raise ValueError('Incomplete replay')
    rows, seen = [], set()
    for index, (selection, reveal) in enumerate(zip(selections, reveals), 1):
        ids, scores = selection['ids'], reveal['measurements']
        if (not ids or len(ids) != len(set(ids)) or seen.intersection(ids) or list(scores) != ids
                or references[index] != ids or not set(ids).issubset(warnings[index]['identifiers'])):
            raise ValueError('Selection, warning group or reveal mismatch')
        seen.update(ids)
        predictions = [selection['prediction_ranges'][identifier]['mean'] for identifier in ids]
        measured = [scores[identifier] for identifier in ids]
        if not all(math.isfinite(value) for value in predictions + measured):
            raise ValueError('Non-finite prediction or measurement')
        coefficient = None
        if len(ids) >= 2 and len(set(predictions)) > 1 and len(set(measured)) > 1:
            coefficient = float(spearmanr(predictions, measured).statistic)
            if not math.isfinite(coefficient):
                raise ValueError('Unexpected undefined correlation')
        rows.append({'round': index, 'warning': warnings[index]['status'], 'batch_size': len(ids),
                     'spearman': coefficient})
    return rows
