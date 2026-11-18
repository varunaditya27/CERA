import copy
import hashlib
import sys
import unittest
from pathlib import Path
from scripts.repair import audit_rule_warning_controls as audit
from scripts.repair import simulate_rule_warnings as simulation
from app.provenance.sources import source_hashes


class RuleWarningControlsTest(unittest.TestCase):
    def test_cases_and_independent_audit(self):
        report = {'script_sha256': hashlib.sha256(Path(simulation.__file__).read_bytes()).hexdigest(),
                  'warning_source_sha256': source_hashes(('warning_checks.py',)), **simulation.simulate()}
        self.assertEqual(report['constraint']['summary']['true_positive'], 7)
        self.assertEqual(report['diversity']['summary']['unavailable'], 1)
        self.assertEqual(audit.audit(report), {'constraint_cases': 10, 'diversity_cases': 5})
        altered = copy.deepcopy(report)
        altered['diversity']['cases'][0]['value'] = 2
        with self.assertRaises(ValueError):
            audit.audit(altered)
        altered = copy.deepcopy(report)
        altered['constraint']['summary']['recall'] = 0
        with self.assertRaises(ValueError):
            audit.audit(altered)

    def test_undefined_precision_and_f1(self):
        result = simulation.summarize([{'label': False, 'status': 'not_triggered'}])
        self.assertIsNone(result['precision'])
        self.assertIsNone(result['recall'])
        self.assertIsNone(result['f1'])


if __name__ == '__main__':
    unittest.main()
