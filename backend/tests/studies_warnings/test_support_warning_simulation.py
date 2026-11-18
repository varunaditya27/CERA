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

from scipy.stats import binom

from app.provenance.sources import source_hashes
from scripts.warnings import audit_support_warning_simulation as audit
from scripts.warnings import simulate_support_warning as simulation


class SupportSimulationTests(unittest.TestCase):
    def test_exact_probabilities_and_reproducibility(self):
        self.assertEqual(simulation.exact_shifted_probability(0.), 0.)
        self.assertEqual(simulation.exact_shifted_probability(1.), 1.)
        for probability in (0.1, 0.5):
            self.assertAlmostEqual(simulation.exact_shifted_probability(probability), binom.sf(2, 10, probability))
        self.assertEqual(simulation.simulate(seed=3, batches=20), simulation.simulate(seed=3, batches=20))
        with self.assertRaises(ValueError):
            simulation.simulate(batches=0)

    def test_audit_detects_altered_distance(self):
        result = {'python': platform.python_version(), 'versions': {name: version(name) for name in ('numpy', 'scipy')},
                  'script_sha256': hashlib.sha256(Path(simulation.__file__).read_bytes()).hexdigest(),
                  'warning_source_sha256': source_hashes(('warning_checks.py',)), **simulation.simulate()}
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'report.json'
            path.write_text(json.dumps(result))
            with patch.object(sys, 'argv', ['audit_support_warning_simulation.py', str(path)]), redirect_stdout(io.StringIO()):
                audit.main()
            result['conditions']['reference']['distances']['c0'] = 5.
            path.write_text(json.dumps(result))
            with patch.object(sys, 'argv', ['audit_support_warning_simulation.py', str(path)]), \
                 self.assertRaisesRegex(ValueError, 'Condition distances'):
                audit.main()


if __name__ == '__main__':
    unittest.main()
