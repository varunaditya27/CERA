import io
import json
import random
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import numpy as np

from app.experiments.hybrid_snapshot import load_hybrid_snapshot

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
import export_hybrid_model


class ExportHybridModelTest(unittest.TestCase):
    def test_final_refit_uses_only_revealed_and_does_not_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            record, specification, output = root / 'run.jsonl', root / 'spec.json', root / 'model.npz'
            ids = [f'id{i:03}' for i in range(60)]
            vectors = {identifier: np.array([i / 60, (i % 7) / 7, (i % 11) / 11], dtype=np.float32)
                       for i, identifier in enumerate(ids)}
            initial = {identifier: float(i / 100) for i, identifier in enumerate(ids[:50])}
            revealed = {identifier: float(i / 100) for i, identifier in enumerate(ids[50:55], start=50)}
            reserved = ids[:20]
            seeds = random.Random(4).sample(range(2**32), 5)
            events = [{'event': 'start', 'initial': initial, 'data_sha256': 'data', 'reference_sha256': 'reference'},
                      {'event': 'method', 'settings': {'reserved_ids': reserved, 'member_seed': 4, 'cv_seed': 7}},
                      {'event': 'method', 'settings': {'member_seeds': seeds}},
                      {'event': 'reveal', 'measurements': revealed}]
            record.write_text(''.join(json.dumps(e) + '\n' for e in events))
            specification.write_text('{}')
            import hashlib
            audit = {'record_sha256': hashlib.sha256(record.read_bytes()).hexdigest()}
            argv = ['export_hybrid_model.py', str(record), str(specification), str(output), '--seed', '7', '--device', 'cpu']
            with patch.object(export_hybrid_model, 'audit_record', return_value=audit), \
                 patch.object(export_hybrid_model, 'load_verified_representations', return_value=vectors), \
                 patch.object(sys, 'argv', argv), redirect_stdout(io.StringIO()):
                export_hybrid_model.main()
            model = load_hybrid_snapshot(output)
            context = model.metadata['context']
            self.assertEqual(set(context['fitting_ids']), (set(initial) | set(revealed)) - set(reserved))
            self.assertFalse(set(context['fitting_ids']) & set(reserved))
            self.assertFalse(set(context['fitting_ids']) & set(ids[55:]))
            self.assertEqual(context['reserved_ids'], reserved)
            self.assertEqual(set(context['neural_fit']['training_ids']) | set(context['neural_fit']['validation_ids']),
                             set(context['fitting_ids']))
            generator = random.Random(4)
            generator.sample(range(2**32), 5)
            self.assertEqual(context['member_seeds'], generator.sample(range(2**32), 5))
            original = output.read_bytes()
            with patch.object(export_hybrid_model, 'audit_record', side_effect=AssertionError('must not run')), \
                 patch.object(sys, 'argv', argv), self.assertRaises(FileExistsError):
                export_hybrid_model.main()
            self.assertEqual(output.read_bytes(), original)


if __name__ == '__main__':
    unittest.main()
