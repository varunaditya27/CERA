import hashlib
import tempfile
import unittest
from pathlib import Path

import numpy as np

from app.experiments.hybrid_predictor import fit_hybrid_group
from app.experiments.hybrid_snapshot import load_hybrid_snapshot, save_hybrid_snapshot
from app.experiments.predictor_group import predict_group


class HybridSnapshotTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ids = [f'i{i:02}' for i in range(30)]
        cls.reserved = [f'held{i}' for i in range(5)]
        cls.vectors = {key: np.array([i / 30, (i % 7) / 7, (i % 11) / 11], dtype=np.float32)
                       for i, key in enumerate(cls.ids + cls.reserved)}
        scores = {key: float(np.sin(i / 5)) for i, key in enumerate(cls.ids)}
        cls.models, _, _ = fit_hybrid_group(cls.vectors, scores, cls.ids, cls.reserved, 7,
                                            [101, 102, 103, 104, 105], 'cpu')

    def test_roundtrip_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'model.npz'
            save_hybrid_snapshot(path, self.models, .25, {'record_sha256': 'example'})
            fingerprint = hashlib.sha256(path.read_bytes()).hexdigest()
            loaded = load_hybrid_snapshot(path, expected_sha256=fingerprint)
            values = np.array([self.vectors[i] for i in self.reserved])
            mean, spread = predict_group(self.models, self.vectors, self.reserved)
            predicted = loaded.predict(values)
            np.testing.assert_allclose(predicted['mean'], mean, rtol=1e-5, atol=1e-6)
            np.testing.assert_allclose(predicted['spread'], spread, rtol=1e-5, atol=1e-6)
            np.testing.assert_allclose(predicted['lower'], mean - .25, rtol=1e-5, atol=1e-6)
            original = path.read_bytes()
            with self.assertRaises(FileExistsError):
                save_hybrid_snapshot(path, self.models, .4, {})
            self.assertEqual(path.read_bytes(), original)
            with self.assertRaises(ValueError):
                load_hybrid_snapshot(path, expected_sha256='wrong')
            for bad in ([], [[1, 2]], [[1, 2, float('nan')]], [['1', '2', '3']], [[True, False, True]]):
                with self.subTest(bad=bad), self.assertRaises(ValueError):
                    loaded.predict(bad)

    def test_rejects_changed_array_and_bad_archive(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'model.npz'
            save_hybrid_snapshot(path, self.models, .25, {})
            with np.load(path, allow_pickle=False) as archive:
                arrays = {name: archive[name] for name in archive.files}
            arrays['ridge_weights'][0, 0] += 1
            modified = Path(temp) / 'modified.npz'
            np.savez_compressed(modified, allow_pickle=False, **arrays)
            with self.assertRaisesRegex(ValueError, 'fingerprint'):
                load_hybrid_snapshot(modified)
            invalid = Path(temp) / 'invalid.npz'
            np.savez_compressed(invalid, allow_pickle=False, surprise=np.array([1]))
            with self.assertRaisesRegex(ValueError, 'contents'):
                load_hybrid_snapshot(invalid)
            with self.assertRaises(ValueError):
                save_hybrid_snapshot(Path(temp) / 'bad.npz', self.models, float('nan'), {})
            with self.assertRaises(ValueError):
                save_hybrid_snapshot(Path(temp) / 'bad.npz', self.models, True, {})


if __name__ == '__main__':
    unittest.main()
