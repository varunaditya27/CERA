import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.provenance.sources import source_hashes


class ProvenanceTests(unittest.TestCase):
    def test_finds_one_source_and_rejects_missing_or_ambiguous_names(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'one').mkdir()
            (root / 'one' / 'module.py').write_text('example')
            with patch('app.provenance.sources.APP', root):
                self.assertEqual(source_hashes(['module.py']),
                                 {'module.py': hashlib.sha256(b'example').hexdigest()})
                with self.assertRaises(ValueError):
                    source_hashes(['missing.py'])
                with self.assertRaises(ValueError):
                    source_hashes(['../module.py'])
                (root / 'two').mkdir()
                (root / 'two' / 'module.py').write_text('different')
                with self.assertRaises(ValueError):
                    source_hashes(['module.py'])
