import sys
import unittest
import hashlib
import io
import json
import platform
import tempfile
from contextlib import redirect_stdout
from importlib.metadata import version
from pathlib import Path
from unittest.mock import patch

from scipy.stats import binom
from app.provenance.sources import source_hashes

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
import simulate_coverage_warning as simulation
import audit_coverage_warning_simulation as audit


class CoverageSimulationTests(unittest.TestCase):
    def test_audit_detects_tampered_count(self):
        result = {'seed': simulation.SEED, 'windows_per_condition': simulation.WINDOWS,
                  'python': platform.python_version(), 'versions': {name: version(name) for name in ('numpy', 'scipy')},
                  'script_sha256': hashlib.sha256(Path(simulation.__file__).read_bytes()).hexdigest(),
                  'warning_source_sha256': source_hashes(('warning_checks.py',)), **simulation.simulate()}
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'report.json'
            path.write_text(json.dumps(result))
            with patch.object(sys, 'argv', ['audit_coverage_warning_simulation.py', str(path)]), redirect_stdout(io.StringIO()):
                audit.main()
            result['conditions']['moderate']['triggered'] += 1
            path.write_text(json.dumps(result))
            with patch.object(sys, 'argv', ['audit_coverage_warning_simulation.py', str(path)]), \
                 self.assertRaisesRegex(ValueError, 'Condition counts'):
                audit.main()

    def test_exact_probabilities_and_reproducibility(self):
        self.assertEqual(simulation.exact_trigger_probability(0.), 1.)
        self.assertEqual(simulation.exact_trigger_probability(1.), 0.)
        for probability in (0.6, 0.8, 0.9):
            self.assertAlmostEqual(simulation.exact_trigger_probability(probability), binom.cdf(22, 30, probability))
        self.assertEqual(simulation.simulate(seed=3, windows=20), simulation.simulate(seed=3, windows=20))
        with self.assertRaises(ValueError):
            simulation.simulate(windows=0)

    def test_unavailable_and_zero_f1_are_not_confused(self):
        with patch.object(simulation, 'coverage_warning', return_value={'status': 'unavailable'}):
            result = simulation.simulate(seed=1, windows=1)
        self.assertEqual(result['conditions']['nominal']['unavailable'], 1)
        self.assertIsNone(result['comparisons']['moderate']['precision'])
        with patch.object(simulation, 'coverage_warning', side_effect=[{'status': 'triggered'},
                          {'status': 'not_triggered'}, {'status': 'not_triggered'}]):
            result = simulation.simulate(seed=1, windows=1)
        self.assertEqual(result['comparisons']['moderate']['f1'], 0.)


if __name__ == '__main__':
    unittest.main()
