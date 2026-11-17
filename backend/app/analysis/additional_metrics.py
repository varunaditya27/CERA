"""Additional descriptive metrics for completed finite-pool searches."""
import itertools
import math

from scipy.stats import spearmanr


def evaluate(events, sequences, scores):
    if not events or events[0].get('event') != 'start' or not scores or set(sequences) != set(scores):
        raise ValueError('Invalid run or eligible pool')
    if any(not math.isfinite(value) for value in scores.values()):
        raise ValueError('Invalid pool score')
    ordered = sorted(scores.values(), reverse=True)
    optimum = ordered[0]
    cutoff = ordered[math.ceil(len(ordered) * 0.01) - 1]
    top = {identifier for identifier, value in scores.items() if value >= cutoff}
    initial = events[0]['initial']
    if not set(initial).issubset(scores) or any(scores[i] != value for i, value in initial.items()):
        raise ValueError('Initial measurements do not match source')
    seen = set(initial)
    initial_top = len(seen & top)
    new_scores, batches, pending = [], [], None
    for event in events[1:]:
        if event['event'] == 'selection':
            if pending is not None:
                raise ValueError('Selection before reveal')
            ids = event['ids']
            if not ids or len(ids) != len(set(ids)) or set(ids) & seen or not set(ids).issubset(scores):
                raise ValueError('Invalid selection')
            pending = event
        elif event['event'] == 'reveal':
            if pending is None or pending['ids'] != list(event['measurements']):
                raise ValueError('Selection and reveal differ')
            ids, measurements = pending['ids'], event['measurements']
            if any(scores[i] != measurements[i] for i in ids):
                raise ValueError('Measurement does not match source')
            strings = [sequences[i] for i in ids]
            if any(not isinstance(s, str) or not s or len(s) != len(strings[0]) for s in strings):
                raise ValueError('Invalid batch sequences')
            distances = [sum(a != b for a, b in zip(left, right))
                         for left, right in itertools.combinations(strings, 2)]
            ranges = pending.get('prediction_ranges')
            correlation = None
            if ranges is not None:
                predicted = [ranges[i]['mean'] for i in ids]
                observed = [measurements[i] for i in ids]
                if any(not math.isfinite(value) for value in predicted):
                    raise ValueError('Invalid prediction')
                if len(ids) >= 2 and len(set(predicted)) > 1 and len(set(observed)) > 1:
                    correlation = float(spearmanr(predicted, observed).statistic)
                    if not math.isfinite(correlation):
                        raise ValueError('Unexpected undefined correlation')
            batches.append({'batch': len(batches) + 1, 'count': len(ids),
                            'mean_pairwise_differences': sum(distances) / len(distances) if distances else None,
                            'prediction_score_spearman': correlation})
            new_scores.extend(measurements[i] for i in ids)
            seen.update(ids)
            pending = None
    if pending is not None:
        raise ValueError('Incomplete selection')
    cumulative = math.fsum(optimum - value for value in new_scores)
    total_top = len(seen & top)
    return {'eligible_count': len(scores), 'top_cutoff': cutoff, 'top_count': len(top),
            'initial_top_found': initial_top, 'new_top_found': total_top - initial_top,
            'total_top_found': total_top, 'top_recall': total_top / len(top),
            'new_measurements': len(new_scores), 'cumulative_regret': cumulative,
            'mean_new_regret': cumulative / len(new_scores) if new_scores else None, 'batches': batches}
