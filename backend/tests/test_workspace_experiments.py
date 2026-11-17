import fcntl
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient
from app.api.main import app
from app.workspace import runs_service as experiments


class WorkspaceExperimentTest(unittest.TestCase):
    def test_real_run_retrieval_and_lock(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(experiments, 'RUNS', Path(directory)):
            client = TestClient(app, client=('127.0.0.1', 50000))
            with (Path(directory) / '.run.lock').open('a') as lock:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                self.assertEqual(client.post('/api/experiments/amylase', json={'seed': 3, 'repair': False}).status_code, 409)
            response = client.post('/api/experiments/amylase', json={'seed': 3, 'repair': False})
            self.assertEqual(response.status_code, 201, response.text)
            result = response.json()
            self.assertEqual(result['new_measurements'], 100)
            self.assertEqual(result['stop_reason'], 'budget_exhausted')
            self.assertNotIn('pool_optimum', result)
            self.assertEqual(client.get('/api/experiments/amylase/' + result['id']).json(), result)
            self.assertEqual(client.get('/api/experiments/amylase').json()[0]['id'], result['id'])
            incomplete = Path(directory) / ('a' * 32)
            incomplete.mkdir()
            listed = client.get('/api/experiments/amylase').json()
            self.assertIn({'status': 'incomplete_or_running', 'id': incomplete.name}, listed)
            self.assertTrue((Path(directory) / result['id'] / 'run.jsonl').is_file())
            self.assertEqual(client.get('/api/experiments/amylase/not-an-id').status_code, 404)
            self.assertEqual(client.post('/api/experiments/amylase', json={'seed': -1}).status_code, 422)
            self.assertEqual(client.post('/api/experiments/amylase', json={'seed': 3, 'repair': 'yes'}).status_code, 422)
            remote = TestClient(app, client=('192.0.2.1', 50000))
            self.assertEqual(remote.post('/api/experiments/amylase', json={'seed': 3}).status_code, 403)
