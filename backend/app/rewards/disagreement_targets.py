"""Identify selected candidates with large member-rank spread in a warning group."""
import numpy as np
from scipy.stats import rankdata


def disagreement_targets(warning, selected):
    selected = list(selected)
    if (not selected or any(not isinstance(i, str) or not i for i in selected)
            or len(selected) != len(set(selected))):
        raise ValueError('Invalid selected identifiers')
    if warning.get('status') not in ('triggered', 'not_triggered', 'unavailable'):
        raise ValueError('Invalid disagreement warning')
    result = {'status': warning['status'], 'threshold': 0.5, 'assessed': {},
              'unassessed': selected.copy(), 'targets': []}
    if warning['status'] != 'triggered':
        return result
    group = warning.get('identifiers')
    members = (warning.get('evidence') or {}).get('members')
    if (not isinstance(group, list) or len(group) < 2 or any(not isinstance(i, str) or not i for i in group)
            or len(group) != len(set(group))
            or not isinstance(members, dict) or set(members) != set(group)):
        raise ValueError('Invalid disagreement group evidence')
    values = np.asarray([members[i] for i in group], dtype=float)
    if (values.shape != (len(group), 5) or not np.isfinite(values).all()
            or np.any(np.ptp(values, axis=0) == 0)):
        raise ValueError('Invalid member predictions')
    ranks = rankdata(values, axis=0, method='average')
    spans = np.ptp(ranks, axis=1) / (len(group) - 1)
    by_id = dict(zip(group, spans))
    result['unassessed'] = [i for i in selected if i not in by_id]
    result['assessed'] = {i: float(by_id[i]) for i in selected if i in by_id}
    result['targets'] = [i for i in selected if i in by_id and by_id[i] >= 0.5]
    return result
