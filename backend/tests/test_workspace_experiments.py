import fcntl
import json
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
            self.assertEqual(result['dataset'], 'amylase')
            self.assertEqual(result['new_measurements'], 100)
            self.assertEqual(result['stop_reason'], 'budget_exhausted')
            self.assertNotIn('pool_optimum', result)
            self.assertEqual(client.get('/api/experiments/amylase/' + result['id']).json(), result)
            self.assertEqual(client.get('/api/experiments/amylase').json()[0]['id'], result['id'])
            incomplete = Path(directory) / ('a' * 32)
            incomplete.mkdir()
            listed = client.get('/api/experiments/amylase').json()
            self.assertIn({'status': 'incomplete_or_running', 'id': incomplete.name}, listed)
            record = Path(directory) / result['id'] / 'run.jsonl'
            self.assertTrue(record.is_file())
            review_url = '/api/experiments/run/' + result['id'] + '/review'
            review = client.get(review_url)
            self.assertEqual(review.status_code, 200, review.text)
            payload = review.json()
            self.assertEqual(sum(len(batch['measurements']) for batch in payload['batches']), 100)
            self.assertEqual(set(payload['batches'][0]['measurements'][0]), {'id', 'score', 'prediction', 'lower', 'upper'})
            self.assertNotIn('prediction_ranges', review.text)
            self.assertNotIn('pool_optimum', review.text)
            self.assertEqual(client.get('/api/experiments/run/' + 'f' * 32 + '/review').status_code, 404)
            events = [json.loads(line) for line in record.read_text().splitlines()]
            reveal = next(event for event in events if event['event'] == 'reveal')
            first = next(iter(reveal['measurements']))
            reveal['measurements'][first] += 1
            record.write_text(''.join(json.dumps(event) + '\n' for event in events))
            self.assertEqual(client.get(review_url).status_code, 409)
            self.assertEqual(client.get('/api/experiments/amylase/not-an-id').status_code, 404)
            self.assertEqual(client.post('/api/experiments/amylase', json={'seed': -1}).status_code, 422)
            self.assertEqual(client.post('/api/experiments/unknown', json={'seed': 3}).status_code, 422)
            self.assertEqual(client.post('/api/experiments/ired', json={'seed': 3, 'predictor': 'mixed'}).status_code, 422)
            self.assertEqual(client.post('/api/experiments/amylase', json={'seed': 3, 'repair': 'yes'}).status_code, 422)
            self.assertEqual(client.post('/api/experiments/amylase', json={'seed': 3, 'gemini': True}).status_code, 422)
            remote = TestClient(app, client=('192.0.2.1', 50000))
            self.assertEqual(remote.post('/api/experiments/amylase', json={'seed': 3}).status_code, 403)
            self.assertEqual(remote.get(review_url).status_code, 403)

    def test_gemini_fallback_is_reported(self):
        from app.llm.gemini_client import GeminiError
        from app.llm.repair_advisor import advise_repair

        def failed_request(*args):
            raise GeminiError('network_error')

        advisor = lambda kind, menu: advise_repair(failed_request, kind, menu)
        with tempfile.TemporaryDirectory() as directory, patch.object(experiments, 'RUNS', Path(directory)):
            with patch('app.llm.local_advisor.local_repair_advisor', return_value=(advisor, 'test-model')):
                client = TestClient(app, client=('127.0.0.1', 50000))
                response = client.post('/api/experiments/amylase', json={'seed': 17, 'repair': True, 'gemini': True})
            self.assertEqual(response.status_code, 201, response.text)
            result = response.json()
            self.assertTrue(result['gemini'])
            self.assertGreater(result['provider_attempts'], 0)
            self.assertEqual(result['provider_attempts'], result['provider_fallbacks'])
            self.assertIsNone(result['reported_total_tokens'])
            self.assertEqual(result['provider_usage_reports'], 0)
            review = client.get('/api/experiments/run/' + result['id'] + '/review')
            self.assertEqual(review.status_code, 200, review.text)
            actions = [action for batch in review.json()['batches'] for action in batch['repairs']]
            self.assertTrue(any(action['attempts'] for action in actions))
            self.assertNotIn('replayed_ids', review.text)

    def test_missing_gemini_configuration_does_not_start_run(self):
        from app.llm.local_advisor import AdvisorConfigurationError
        with tempfile.TemporaryDirectory() as directory, patch.object(experiments, 'RUNS', Path(directory)):
            with patch('app.llm.local_advisor.local_repair_advisor', side_effect=AdvisorConfigurationError):
                response = TestClient(app, client=('127.0.0.1', 50000)).post(
                    '/api/experiments/amylase', json={'seed': 1, 'repair': True, 'gemini': True})
            self.assertEqual(response.status_code, 503)
            self.assertEqual(list(Path(directory).glob('*/run.jsonl')), [])

    def test_reported_tokens_are_counted_only_when_present(self):
        from app.llm.repair_advisor import advise_repair

        advisor = lambda kind, menu: advise_repair(lambda warning, options: ('{"option":0}', {'totalTokenCount': 10}), kind, menu)
        with tempfile.TemporaryDirectory() as directory, patch.object(experiments, 'RUNS', Path(directory)):
            with patch('app.llm.local_advisor.local_repair_advisor', return_value=(advisor, 'test-model')):
                response = TestClient(app, client=('127.0.0.1', 50000)).post(
                    '/api/experiments/amylase', json={'seed': 17, 'repair': True, 'gemini': True})
            self.assertEqual(response.status_code, 201, response.text)
            result = response.json()
            self.assertGreater(result['provider_attempts'], 0)
            self.assertEqual(result['provider_usage_reports'], result['provider_attempts'])
            self.assertEqual(result['reported_total_tokens'], 10 * result['provider_usage_reports'])
            self.assertEqual(result['provider_fallbacks'], 0)

    def test_other_proteins_use_their_own_sources(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(experiments, 'RUNS', Path(directory)):
            client = TestClient(app, client=('127.0.0.1', 50000))
            for dataset in ('ired', 'hydro-P06241', 'hydro-P01053', 'hydro-P0A9X9'):
                with self.subTest(dataset=dataset):
                    response = client.post('/api/experiments/' + dataset, json={'seed': 3, 'repair': False})
                    self.assertEqual(response.status_code, 201, response.text)
                    self.assertEqual(response.json()['dataset'], dataset)
                    self.assertEqual(response.json()['new_measurements'], 100)
                    self.assertEqual(response.json()['range_count'], 100)
                    if dataset in ('ired', 'hydro-P06241'):
                        audit = client.get('/api/experiments/run/' + response.json()['id'] + '/audit')
                        self.assertEqual(audit.status_code, 200, audit.text)
                        self.assertEqual(audit.json()['selections_checked'], 10)

    def test_mixed_predictor_uses_recorded_cpu_fallback(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(experiments, 'RUNS', Path(directory)):
            with patch('torch.cuda.is_available', return_value=False):
                client = TestClient(app, client=('127.0.0.1', 50000))
                response = client.post('/api/experiments/amylase', json={'seed': 17, 'repair': True, 'predictor': 'mixed'})
            self.assertEqual(response.status_code, 201, response.text)
            result = response.json()
            self.assertEqual((result['predictor'], result['device']), ('mixed', 'cpu'))
            record = Path(directory) / result['id'] / 'run.jsonl'
            events = [json.loads(line) for line in record.read_text().splitlines()]
            settings = next(event['settings'] for event in events if event['event'] == 'method')
            self.assertEqual((settings['method'], settings['hybrid_device']), ('esm_hybrid_reward', 'cpu'))
            review = client.get('/api/experiments/run/' + result['id'] + '/review')
            self.assertEqual(review.status_code, 200, review.text)
            self.assertEqual(review.json()['summary']['device'], 'cpu')
            audit = client.get('/api/experiments/run/' + result['id'] + '/audit')
            self.assertEqual(audit.status_code, 200, audit.text)
            self.assertGreater(audit.json()['selections_checked'], 0)
            summary_path = Path(directory) / result['id'] / 'summary.json'
            summary = json.loads(summary_path.read_text())
            summary['device'] = 'cuda'
            summary_path.write_text(json.dumps(summary))
            self.assertEqual(client.get('/api/experiments/run/' + result['id'] + '/review').status_code, 409)
