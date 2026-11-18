import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from scripts.hybrid.audit_mixed_heldout import main


class AuditMixedHeldoutTests(unittest.TestCase):
    def test_rejects_evaluation_for_different_predictions(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            predictions, evaluation, output = (root / name for name in ('predictions.json', 'evaluation.json', 'audit.json'))
            predictions.write_text(json.dumps({'hybrid_configuration': {}}))
            evaluation.write_text(json.dumps({'predictions_sha256': 'changed'}))
            with patch('scripts.hybrid.audit_mixed_heldout.hybrid_configuration', return_value={}), \
                    patch.object(sys, 'argv', ['audit', str(predictions), str(evaluation), str(output)]):
                with self.assertRaisesRegex(ValueError, 'Fingerprint or dataset mismatch'):
                    main()
            self.assertFalse(output.exists())


if __name__ == '__main__':
    unittest.main()
