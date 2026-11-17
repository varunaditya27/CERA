import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient
from app.api.main import app
from app.workspace import runs_service


class LocalDecisionAuditTest(unittest.TestCase):
    def test_real_run_and_altered_ranking(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(runs_service, 'RUNS', Path(directory)):
            client = TestClient(app, client=('127.0.0.1', 50000))
            response = client.post('/api/experiments/amylase', json={'seed': 17, 'repair': True})
            self.assertEqual(response.status_code, 201, response.text)
            run_id = response.json()['id']
            audit_url = '/api/experiments/run/' + run_id + '/audit'
            audit = client.get(audit_url)
            self.assertEqual(audit.status_code, 200, audit.text)
            self.assertGreater(audit.json()['selections_checked'], 0)
            self.assertGreater(audit.json()['repair_replays_checked'], 0)
            self.assertFalse(audit.json()['predictors_refitted'])
            path = Path(directory) / run_id / 'run.jsonl'
            original = path.read_text()
            events = [json.loads(line) for line in original.splitlines()]
            selection = next(event for event in events if event['event'] == 'selection')
            reveal = next(event for event in events if event['event'] == 'reveal')
            selection['ids'][0], selection['ids'][1] = selection['ids'][1], selection['ids'][0]
            reveal['measurements'] = {i: reveal['measurements'][i] for i in selection['ids']}
            path.write_text(''.join(json.dumps(event) + '\n' for event in events))
            self.assertEqual(client.get('/api/experiments/run/' + run_id + '/review').status_code, 200)
            self.assertEqual(client.get(audit_url).status_code, 409)
            events = [json.loads(line) for line in original.splitlines()]
            distances = next(event['settings']['reward_distance'] for event in events if event['event'] == 'method' and 'reward_distance' in event['settings'])
            distances['scale'] *= 2
            path.write_text(''.join(json.dumps(event) + '\n' for event in events))
            self.assertEqual(client.get('/api/experiments/run/' + run_id + '/review').status_code, 200)
            self.assertEqual(client.get(audit_url).status_code, 409)
            events = [json.loads(line) for line in original.splitlines()]
            setup = next(event['settings'] for event in events if event['event'] == 'method')
            name = next(iter(setup['source_sha256']))
            setup['source_sha256'][name] = '0' * 64
            path.write_text(''.join(json.dumps(event) + '\n' for event in events))
            self.assertEqual(client.get(audit_url).status_code, 409)
            path.write_text(original)
            with patch('app.features.amylase_representations.load_verified_representations', side_effect=FileNotFoundError):
                self.assertEqual(client.get(audit_url).status_code, 409)
            with patch('app.api.web_experiments.audit_run', side_effect=ImportError):
                self.assertEqual(client.get(audit_url).status_code, 409)
            self.assertEqual(TestClient(app, client=('192.0.2.1', 50000)).get(audit_url).status_code, 403)
