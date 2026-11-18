import hashlib
import io
import json
import platform
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from importlib.metadata import version
from pathlib import Path
from unittest.mock import patch

from app.provenance.sources import source_hashes
from scripts.warnings import audit_disagreement_warning_simulation as audit
from scripts.warnings import simulate_disagreement_warning as simulation


class DisagreementSimulationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = {'python': platform.python_version(),
                      'versions': {name: version(name) for name in ('numpy', 'scipy')},
                      'script_sha256': hashlib.sha256(Path(simulation.__file__).read_bytes()).hexdigest(),
                      'warning_source_sha256': source_hashes(('warning_checks.py',)), **simulation.simulate()}

    def test_planted_conditions_and_undefined_precision(self):
        conditions = self.result['conditions']
        self.assertEqual([conditions[name]['triggered'] for name in ('identical', 'swapped', 'reversed')], [0, 0, 45])
        self.assertIsNone(self.result['comparisons']['swapped']['precision'])
        self.assertEqual(self.result['comparisons']['swapped']['f1'], 0.)
        self.assertEqual(audit.rank([2, 1, 1]), [3., 1.5, 1.5])
        self.assertAlmostEqual(audit.correlation([1, 2, 3], [3, 2, 1]), -1.)

    def test_audit_rejects_changed_member(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'report.json'
            path.write_text(json.dumps(self.result))
            with patch.object(sys, 'argv', ['audit_disagreement_warning_simulation.py', str(path)]), redirect_stdout(io.StringIO()):
                audit.main()
            tampered = json.loads(path.read_text())
            tampered['cases'][0]['members']['0'][0] += 1
            path.write_text(json.dumps(tampered))
            with patch.object(sys, 'argv', ['audit_disagreement_warning_simulation.py', str(path)]), \
                 self.assertRaisesRegex(ValueError, 'Planted case'):
                audit.main()


if __name__ == '__main__':
    unittest.main()
