import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import torch

from app.features.representation_cache import load_cache, save_cache
from app.features.representations import FEATURES, represent, sequence_id


class FakeTokenizer:
    def __call__(self, sequences, **kwargs):
        length = max(len(sequence) for sequence in sequences) + 2
        ids, attention, special = [], [], []
        for sequence in sequences:
            row = [21] + [ord(letter) - 64 for letter in sequence] + [22]
            padding = length - len(row)
            ids.append(row + [0] * padding)
            attention.append([1] * len(row) + [0] * padding)
            special.append([1] + [0] * len(sequence) + [1] + [1] * padding)
        return {'input_ids': torch.tensor(ids), 'attention_mask': torch.tensor(attention),
                'special_tokens_mask': torch.tensor(special)}


class FakeModel:
    config = SimpleNamespace(max_position_embeddings=8)

    def to(self, **kwargs):
        return self

    def eval(self):
        return self

    def __call__(self, input_ids, attention_mask):
        return SimpleNamespace(last_hidden_state=input_ids.float().unsqueeze(-1).repeat(1, 1, FEATURES))


class RepresentationTests(unittest.TestCase):
    def test_residue_only_pooling_and_padding(self):
        short, long = 'AC', 'ACDE'
        inputs = {sequence_id(short): short, sequence_id(long): long}
        batch = represent(inputs, FakeTokenizer(), FakeModel(), 'cpu')
        alone = represent({sequence_id(short): short}, FakeTokenizer(), FakeModel(), 'cpu')
        self.assertEqual(batch.shape, (2, FEATURES))
        self.assertTrue(np.isfinite(batch).all())
        np.testing.assert_array_equal(batch[0], alone[0])
        self.assertEqual(float(batch[0, 0]), 2.0)

    def test_rejects_invalid_or_mismatched_sequences_and_truncation(self):
        for inputs in ({'wrong': 'AC'}, {'x': ''}, {'x': 'AXB'}, {sequence_id('ACDEFGH'): 'ACDEFGH'}):
            with self.subTest(inputs=inputs), self.assertRaises(ValueError):
                represent(inputs, FakeTokenizer(), FakeModel(), 'cpu')
        with self.assertRaises(ValueError):
            represent({sequence_id('AC'): 'AC'}, FakeTokenizer(), FakeModel(), 'cpu', batch_size=0)

    def test_rejects_lost_residues_and_nonfinite_output(self):
        class TruncatingTokenizer(FakeTokenizer):
            def __call__(self, sequences, **kwargs):
                result = super().__call__(sequences, **kwargs)
                result['attention_mask'][0, 1] = 0
                return result

        class NonfiniteModel(FakeModel):
            def __call__(self, input_ids, attention_mask):
                result = super().__call__(input_ids, attention_mask)
                result.last_hidden_state[0, 1, 0] = float('nan')
                return result

        inputs = {sequence_id('AC'): 'AC'}
        for tokenizer, model in ((TruncatingTokenizer(), FakeModel()), (FakeTokenizer(), NonfiniteModel())):
            with self.assertRaises(ValueError):
                represent(inputs, tokenizer, model, 'cpu')

    def test_cache_integrity_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'cache.npz'
            ids = [sequence_id('AC'), sequence_id('ACD')]
            values = np.arange(2 * FEATURES, dtype=np.float32).reshape(2, FEATURES)
            settings = {'revision': 'fixed', 'dataset_sha256': 'source'}
            save_cache(path, ids, values, settings)
            np.testing.assert_array_equal(load_cache(path, ids, settings), values)
            before = path.read_bytes()
            with self.assertRaises(FileExistsError):
                save_cache(path, ids, values, settings)
            self.assertEqual(path.read_bytes(), before)
            for wrong_ids, wrong_settings in ((ids[::-1], settings), (ids, {'revision': 'changed'})):
                with self.assertRaises(ValueError):
                    load_cache(path, wrong_ids, wrong_settings)
            with self.assertRaises(ValueError):
                save_cache(Path(directory) / 'duplicate.npz', ids[:1] * 2, values, settings)
            invalid = values.copy()
            invalid[0, 0] = np.nan
            with self.assertRaises(ValueError):
                save_cache(Path(directory) / 'invalid.npz', ids, invalid, settings)
            with np.load(path, allow_pickle=False) as archive:
                metadata = archive['metadata'].copy()
            tampered = values.copy()
            tampered[0, 0] += 1
            np.savez(Path(directory) / 'tampered.npz', identifiers=np.asarray(ids), vectors=tampered, metadata=metadata)
            with self.assertRaises(ValueError):
                load_cache(Path(directory) / 'tampered.npz', ids, settings)


if __name__ == '__main__':
    unittest.main()
