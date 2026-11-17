import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient
from app.api.main import app


class ResultsApiTest(unittest.TestCase):
    def test_pinned_audit_and_unavailable_file(self):
        client = TestClient(app)
        response = client.get('/api/results/mixed-search')
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual((result['pairs'], result['ties']), (10, 10))
        self.assertEqual((result['methods']['mixed']['covered'], result['methods']['mixed']['measured']), (878, 1000))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'audit.json'
            path.write_text('{}')
            with patch('app.api.results.AUDIT', path):
                self.assertEqual(client.get('/api/results/mixed-search').status_code, 503)
                path.unlink()
                self.assertEqual(client.get('/api/results/mixed-search').status_code, 503)
