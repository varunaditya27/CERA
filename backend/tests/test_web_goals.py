import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient
from app.api.main import app
from app.workspace import goals_service, runs_service


class WebGoalTest(unittest.TestCase):
    def test_compile_review_run_and_changed_goal(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch.object(goals_service, 'GOALS', root / 'goals'), patch.object(runs_service, 'RUNS', root / 'runs'):
                with patch.object(goals_service, 'local_gemini_configuration', return_value=('test-key', 'test-model')):
                    with patch.object(goals_service, 'request_goal', return_value=(json.dumps({
                        'supported': True, 'uncertainty_penalty': 0.2, 'distance_penalty': 0.3, 'diversity_bonus': 0.4}), {'totalTokenCount': 12})):
                        client = TestClient(app, client=('127.0.0.1', 50000))
                        response = client.post('/api/goals', json={'goal': 'Maximize fitness with diverse batches'})
                self.assertEqual(response.status_code, 201, response.text)
                goal = response.json()
                self.assertNotIn('test-key', response.text)
                self.assertEqual(goal['specification']['terms']['diversity_bonus']['weight'], 0.4)
                self.assertEqual(client.get('/api/goals').json()[0]['sha256'], goal['sha256'])
                body = {'seed': 3, 'goal_id': goal['id'], 'goal_sha256': goal['sha256']}
                run = client.post('/api/experiments/amylase', json=body)
                self.assertEqual(run.status_code, 201, run.text)
                self.assertEqual(run.json()['goal_id'], goal['id'])
                events = [json.loads(line) for line in (root / 'runs' / run.json()['id'] / 'run.jsonl').read_text().splitlines()]
                settings = next(event['settings'] for event in events if event['event'] == 'method')
                self.assertEqual(settings['reward_spec'], goal['specification'])
                self.assertEqual(settings['reward_origin']['input_sha256'], goal['sha256'])
                review = client.get('/api/experiments/run/' + run.json()['id'] + '/review')
                self.assertEqual(review.status_code, 200, review.text)
                self.assertEqual(review.json()['goal'], goal['input_goal'])
                self.assertEqual(review.json()['specification'], goal['specification'])
                goal_path = root / 'goals' / (goal['id'] + '.json')
                goal_path.write_text(goal_path.read_text() + ' ')
                self.assertEqual(client.post('/api/experiments/amylase', json=body).status_code, 409)
                self.assertEqual(client.post('/api/experiments/amylase', json={'seed': 3, 'goal_id': goal['id']}).status_code, 422)
                self.assertEqual(TestClient(app, client=('192.0.2.1', 123)).get('/api/goals').status_code, 403)

    def test_unsupported_goal_is_not_saved(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(goals_service, 'GOALS', Path(directory)):
            with patch.object(goals_service, 'local_gemini_configuration', return_value=('test-key', 'test-model')):
                with patch.object(goals_service, 'request_goal', return_value=(json.dumps({
                    'supported': False, 'uncertainty_penalty': 0.2, 'distance_penalty': 0.3, 'diversity_bonus': 0.4}), {})):
                    response = TestClient(app, client=('127.0.0.1', 50000)).post('/api/goals', json={'goal': 'Minimize fitness'})
            self.assertEqual(response.status_code, 422)
            self.assertEqual(list(Path(directory).glob('*.json')), [])
