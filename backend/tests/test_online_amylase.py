import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.features import online_amylase


class OnlineAmylaseTest(unittest.TestCase):
    def test_changed_cache_is_rejected_before_loading_model(self):
        online_amylase._encoder.cache_clear()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'cache.npz'
            path.write_bytes(b'changed')
            with patch.object(online_amylase, 'CACHE', path):
                with self.assertRaisesRegex(ValueError, 'cache fingerprint mismatch'):
                    online_amylase._encoder()
