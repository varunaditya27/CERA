"""Track later range coverage for an accepted reward change."""
import copy

from app.rewards.reward_spec import validate_spec


class RollbackMonitor:
    def __init__(self):
        self.pending = None

    def register(self, previous, current, round_number):
        validate_spec(previous)
        validate_spec(current)
        if (previous == current or any(previous[key] != current[key] for key in
                                       ('goal', 'hard_constraints', 'budget', 'abstain_after_failed_repairs'))
                or any(previous['terms'][key]['allowed_range'] != current['terms'][key]['allowed_range']
                       for key in previous['terms'])
                or not isinstance(round_number, int) or isinstance(round_number, bool) or round_number < 1):
            raise ValueError('Invalid accepted reward change')
        events = []
        if self.pending is not None:
            if previous != self.pending['current'] or round_number < self.pending['last_observed_round']:
                raise ValueError('Accepted reward lineage mismatch')
            events.append({'status': 'superseded', **copy.deepcopy(self.pending)})
        self.pending = {'accepted_round': round_number, 'previous': copy.deepcopy(previous),
                        'current': copy.deepcopy(current), 'last_observed_round': round_number, 'observations': []}
        events.append({'status': 'monitoring', **copy.deepcopy(self.pending)})
        return events

    def observe(self, current, round_number, observations):
        if self.pending is None:
            return current, []
        if (current != self.pending['current'] or not isinstance(round_number, int) or isinstance(round_number, bool)
                or round_number <= self.pending['last_observed_round']):
            raise ValueError('Rollback observation lineage mismatch')
        rows = list(observations)
        seen = {row['id'] for row in self.pending['observations']}
        if (not rows or any(not isinstance(i, str) or not i or not isinstance(covered, bool) for i, covered in rows)
                or len({i for i, _ in rows}) != len(rows) or seen.intersection(i for i, _ in rows)):
            raise ValueError('Invalid rollback observations')
        self.pending['last_observed_round'] = round_number
        selected = rows[:30 - len(self.pending['observations'])]
        self.pending['observations'].extend({'id': i, 'covered': covered} for i, covered in selected)
        if len(self.pending['observations']) < 30:
            return current, [{'status': 'pending', 'accepted_round': self.pending['accepted_round'],
                              'observed': len(self.pending['observations'])}]
        covered = sum(row['covered'] for row in self.pending['observations'])
        state = copy.deepcopy(self.pending)
        self.pending = None
        should_rollback = covered < 0.75 * 30
        result = copy.deepcopy(state['previous'] if should_rollback else state['current'])
        return result, [{'status': 'rolled_back' if should_rollback else 'retained',
                         'covered': covered, **state}]

    def finish(self):
        if self.pending is None:
            return []
        state, self.pending = copy.deepcopy(self.pending), None
        return [{'status': 'insufficient_followup', **state}]
