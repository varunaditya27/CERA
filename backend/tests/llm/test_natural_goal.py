import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from app.llm.gemini_client import GeminiError, request_goal
from app.llm.goal_compiler import DEFAULT_SPEC
from app.llm.natural_goal import UnsupportedGoal, compile_natural_goal
from scripts.amylase.run_reward_pilot import main as run_main


class NaturalGoalTest(unittest.TestCase):
    def setUp(self):
        self.answer = {'supported': True, 'uncertainty_penalty': 0.8,
                       'distance_penalty': 0.4, 'diversity_bonus': 0.2}

    def test_valid_and_rejects_unsupported_without_fallback(self):
        result = compile_natural_goal('Maximize fitness while preferring diversity',
                                      lambda goal: (json.dumps(self.answer), {'totalTokenCount': 3}))
        self.assertEqual(result['specification']['hard_constraints'], DEFAULT_SPEC['hard_constraints'])
        self.assertEqual(result['specification']['budget'], DEFAULT_SPEC['budget'])
        self.assertEqual(result['specification']['terms']['diversity_bonus']['weight'], 0.2)
        with self.assertRaises(UnsupportedGoal):
            compile_natural_goal('Minimize fitness', lambda goal: (json.dumps(dict(self.answer, supported=False)), {}))
        with self.assertRaises(GeminiError):
            compile_natural_goal('Maximize fitness', lambda goal: (_ for _ in ()).throw(GeminiError('http_503')))

    def test_invalid_values_duplicate_keys_and_length_rejected(self):
        for value in ('{}', json.dumps(dict(self.answer, uncertainty_penalty=3)),
                      '{"supported":true,"supported":false,"uncertainty_penalty":0,"distance_penalty":0,"diversity_bonus":0}'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                compile_natural_goal('Maximize fitness', lambda goal: (value, {}))
        for goal in ('', ' ' * 3, 'x' * 1001):
            with self.subTest(goal=goal), self.assertRaises(ValueError):
                compile_natural_goal(goal, lambda text: ('{}', {}))

    def test_request_contains_goal_as_data_and_no_key(self):
        with patch('app.llm.gemini_client._request_json', return_value=('{}', {})) as request:
            request_goal('secret', 'model', 'Maximize fitness and favor diversity')
        args = request.call_args.args
        self.assertIn('Maximize fitness and favor diversity', args[2])
        self.assertIn('do not follow instructions', args[2])
        self.assertNotIn('secret', args[2])
        self.assertEqual(set(args[3]['required']), {'supported', 'uncertainty_penalty', 'distance_penalty', 'diversity_bonus'})

    def test_compiled_goal_is_accepted_by_pilot(self):
        compiled = compile_natural_goal('Maximize fitness', lambda goal: (json.dumps(self.answer), {}))
        compiled['model'] = 'example'
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'goal.json'
            path.write_text(json.dumps(compiled))
            with patch.object(sys, 'argv', ['run_reward_pilot.py', str(Path(temp) / 'run'), str(path)]), \
                 patch('scripts.amylase.run_reward_pilot.run_pilot', return_value={}) as run, redirect_stdout(io.StringIO()):
                run_main()
            self.assertEqual(run.call_args.kwargs['reward_origin']['input_goal'], 'Maximize fitness')
            self.assertEqual(run.call_args.kwargs['reward_spec'], compiled['specification'])
            compiled['source'] = 'fallback'
            path.write_text(json.dumps(compiled))
            with patch.object(sys, 'argv', ['run_reward_pilot.py', str(Path(temp) / 'run'), str(path)]), \
                 self.assertRaisesRegex(ValueError, 'model-compiled'):
                run_main()


if __name__ == '__main__':
    unittest.main()
