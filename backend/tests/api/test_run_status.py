import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

from app.workspace import runs_service


class RunStatusTest(unittest.TestCase):
    def test_active_then_failed_run_and_legacy_record(self):
        first = threading.Event()
        create = threading.Event()
        created = threading.Event()
        finish = threading.Event()

        def interrupted_pilot(directory, **kwargs):
            first.set()
            if not create.wait(10):
                raise RuntimeError('test timed out')
            directory.mkdir()
            created.set()
            if not finish.wait(10):
                raise RuntimeError('test timed out')
            raise RuntimeError('simulated interruption')

        with tempfile.TemporaryDirectory() as directory, patch.object(runs_service, 'RUNS', Path(directory)):
            with patch('app.experiments.prediction_pilot.run_pilot', side_effect=interrupted_pilot):
                with ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(runs_service.run_experiment, 7, False)
                    try:
                        self.assertTrue(first.wait(10))
                        pending = runs_service.list_experiments()
                        self.assertEqual(len(pending), 1)
                        self.assertEqual(pending[0]['status'], 'running')
                        create.set()
                        self.assertTrue(created.wait(10))
                        self.assertEqual(runs_service.list_experiments(), pending)
                    finally:
                        create.set()
                        finish.set()
                    with self.assertRaisesRegex(RuntimeError, 'simulated interruption'):
                        future.result(timeout=10)
            self.assertEqual(runs_service.list_experiments(), [{'status': 'incomplete', 'id': pending[0]['id']}])
            old = Path(directory) / ('b' * 32)
            old.mkdir()
            self.assertIn({'status': 'incomplete_or_running', 'id': old.name}, runs_service.list_experiments())

    def test_lock_released_when_worker_process_exits(self):
        import selectors
        import subprocess
        import sys

        with tempfile.TemporaryDirectory() as directory, patch.object(runs_service, 'RUNS', Path(directory)):
            run_id = 'c' * 32
            (Path(directory) / run_id).mkdir()
            markers = Path(directory) / '.active'
            markers.mkdir()
            marker = markers / run_id
            marker.touch()
            code = ('import fcntl,sys,time; f=open(sys.argv[1], "r+"); '
                    'fcntl.flock(f, fcntl.LOCK_EX); print("ready", flush=True); time.sleep(60)')
            process = subprocess.Popen([sys.executable, '-c', code, str(marker)], stdout=subprocess.PIPE, text=True)
            try:
                with selectors.DefaultSelector() as selector:
                    selector.register(process.stdout, selectors.EVENT_READ)
                    self.assertTrue(selector.select(timeout=10))
                    self.assertEqual(process.stdout.readline().strip(), 'ready')
                self.assertEqual(runs_service.list_experiments(), [{'status': 'running', 'id': run_id}])
            finally:
                process.terminate()
                process.wait(timeout=10)
                process.stdout.close()
            self.assertEqual(runs_service.list_experiments(), [{'status': 'incomplete', 'id': run_id}])
