"""Independently reconstruct later-coverage rollback events from a run record."""
import copy


def audit_rollback_events(events):
    setup = next(e['settings'] for e in events if e['event'] == 'method')
    if setup.get('rollback_monitor') is not True:
        raise ValueError('Rollback monitor was not enabled')
    spec, pending, selection, expected = copy.deepcopy(setup['reward_spec']), None, None, []
    batch, stopped, rolled_back_round = 0, False, None
    counts = {'monitoring': 0, 'pending': 0, 'superseded': 0, 'rolled_back': 0,
              'retained': 0, 'insufficient_followup': 0}
    for event in events:
        kind = event['event']
        if kind == 'selection':
            if expected or selection is not None or stopped:
                raise ValueError('Invalid rollback selection chronology')
            selection = event
        elif kind == 'reveal':
            if selection is None or expected or selection['ids'] != list(event['measurements']):
                raise ValueError('Invalid rollback reveal chronology')
            batch += 1
            if pending is not None:
                rows = [{'id': identifier, 'covered': selection['prediction_ranges'][identifier]['lower'] <= score <=
                         selection['prediction_ranges'][identifier]['upper']}
                        for identifier, score in event['measurements'].items()]
                pending['last_observed_round'] = batch
                pending['observations'].extend(rows[:30 - len(pending['observations'])])
                if len(pending['observations']) < 30:
                    expected.append({'status': 'pending', 'accepted_round': pending['accepted_round'],
                                     'observed': len(pending['observations'])})
                else:
                    covered = sum(row['covered'] for row in pending['observations'])
                    rollback = covered < 22.5
                    expected.append({'status': 'rolled_back' if rollback else 'retained',
                                     'covered': covered, **copy.deepcopy(pending)})
                    spec = copy.deepcopy(pending['previous'] if rollback else pending['current'])
                    pending = None
                    if rollback:
                        rolled_back_round = batch
            selection = None
            stopped = event['stop_reason'] is not None
        elif kind == 'stop':
            if expected:
                raise ValueError('Missing rollback events before stop')
            stopped = True
        elif kind == 'method' and 'repair_actions' in event['settings']:
            state = event['settings']
            if expected or state['round'] != batch or rolled_back_round == batch or stopped:
                raise ValueError('Invalid repair chronology during monitoring')
            for action in state['repair_actions']:
                if action['status'] != 'accepted':
                    continue
                current = copy.deepcopy(action['specification'])
                if pending is not None:
                    expected.append({'status': 'superseded', **copy.deepcopy(pending)})
                pending = {'accepted_round': batch, 'previous': copy.deepcopy(spec), 'current': current,
                           'last_observed_round': batch, 'observations': []}
                expected.append({'status': 'monitoring', **copy.deepcopy(pending)})
                spec = current
        elif kind == 'method' and 'rollback_events' in event['settings']:
            if event['settings']['round'] != batch:
                raise ValueError('Rollback event round mismatch')
            actual = event['settings']['rollback_events']
            if not expected and stopped and pending is not None:
                expected.append({'status': 'insufficient_followup', **copy.deepcopy(pending)})
                pending = None
            if not actual or actual != expected[:len(actual)]:
                raise ValueError('Rollback event evidence mismatch')
            for item in actual:
                counts[item['status']] += 1
            del expected[:len(actual)]
    if not stopped or selection is not None or expected or pending is not None:
        raise ValueError('Incomplete rollback monitoring record')
    return counts
