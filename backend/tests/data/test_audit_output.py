import tempfile
import unittest
from pathlib import Path

from app.provenance.audit_output import write_new_or_confirm_saved
from app.provenance.sources import CodeChanged, require_recorded_code


class AuditOutputTests(unittest.TestCase):
    def test_writes_then_confirms_then_rejects_a_different_result(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'audit.json'
            self.assertEqual(write_new_or_confirm_saved(path, {'runs': 3, 'audit_script_sha256': 'a'}), 'written')
            self.assertEqual(write_new_or_confirm_saved(path, {'runs': 3, 'audit_script_sha256': 'b'}),
                             'matches the saved audit record')
            with self.assertRaises(ValueError):
                write_new_or_confirm_saved(path, {'runs': 4, 'audit_script_sha256': 'a'})

    def test_changed_code_raises_with_the_legacy_hint(self):
        require_recorded_code(True, True)
        with self.assertRaisesRegex(CodeChanged, 'legacy_audit'):
            require_recorded_code(True, False)


if __name__ == '__main__':
    unittest.main()
