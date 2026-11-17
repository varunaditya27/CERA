import unittest
from unittest.mock import patch

import numpy as np
from fastapi.testclient import TestClient
from app.api.main import app
from app.api.predictions import prediction_resources
from app.datasets.amylase import DATA


class PredictionApiTest(unittest.TestCase):
    def test_real_prediction_and_invalid_requests(self):
        import csv
        with DATA.open(newline='', encoding='utf-8') as file:
            sequence = next(csv.DictReader(file))['sequence']
        client = TestClient(app)
        result = client.post('/api/predictions/amylase', json={'sequence': sequence})
        self.assertEqual(result.status_code, 200)
        body = result.json()
        self.assertEqual(set(body), {'mean', 'lower', 'upper', 'observed_role', 'model_sha256'})
        self.assertTrue(np.isfinite([body['mean'], body['lower'], body['upper']]).all())
        self.assertLessEqual(body['lower'], body['mean'])
        self.assertLessEqual(body['mean'], body['upper'])
        self.assertEqual(client.post('/api/predictions/amylase', json={'sequence': 'BAD!'}).status_code, 422)
        self.assertEqual(client.post('/api/predictions/amylase', json={'sequence': sequence, 'score': 1}).status_code, 422)
        self.assertEqual(client.post('/api/predictions/amylase', json={'sequence': 'A'}).status_code, 422)
        model, _, reference = prediction_resources()
        with patch('app.api.predictions.prediction_resources', return_value=(model, {}, reference)):
            self.assertEqual(client.post('/api/predictions/amylase', json={'sequence': reference}).status_code, 404)
        with patch('app.api.predictions.prediction_resources', side_effect=ValueError('bad source')):
            self.assertEqual(client.post('/api/predictions/amylase', json={'sequence': sequence}).status_code, 503)
