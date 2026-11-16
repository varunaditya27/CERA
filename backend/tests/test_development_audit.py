import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
from audit_development_repairs import check_summary, check_targets


class DevelopmentAuditTests(unittest.TestCase):
    def test_target_evidence_detects_changed_target_and_assessment(self):
        warning = {'status': 'triggered', 'identifiers': ['a', 'b', 'c'], 'evidence': {'members': {
            'a': [1, 3, 1, 3, 1], 'b': [2, 2, 2, 2, 2], 'c': [3, 1, 3, 1, 3]}}}
        evidence = {'status': 'triggered', 'threshold': 0.5, 'assessed': {'a': 1.0, 'b': 0.0},
                    'targets': ['a'], 'unassessed': ['outside']}
        check_targets(warning, evidence, ['a', 'b', 'outside'])
        for change in ('targets', 'assessed', 'unassessed'):
            altered = copy.deepcopy(evidence)
            altered[change] = {} if change == 'assessed' else []
            with self.assertRaises(ValueError):
                check_targets(warning, altered, ['a', 'b', 'outside'])

    def test_summary_detects_changed_score_coverage_and_stop(self):
        row = {'status': 'completed', 'new_measurements': '1', 'best_observed': '2.0', 'pool_regret': '0.0',
               'found_top_one_percent': 'True', 'stop_reason': 'budget_exhausted', 'range_count': '1',
               'covered': '1', 'mean_range_width': '2.0'}
        args = ({'a': 1.0, 'b': 2.0}, 1, 'budget_exhausted', 1, [2.0], {'a': 1.0, 'b': 2.0})
        check_summary(row, *args)
        for field, value in (('best_observed', '1.0'), ('covered', '0'), ('stop_reason', 'failed_repairs')):
            altered = dict(row, **{field: value})
            with self.assertRaises(ValueError):
                check_summary(altered, *args)
