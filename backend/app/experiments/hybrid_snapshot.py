"""Store and use mixed predictors as validated numeric arrays, without pickle."""
import hashlib
import json
import os
import tempfile
from pathlib import Path

import numpy as np

FORMAT = 'cera-hybrid-v1'
PARAMETERS = ('0.weight', '0.bias', '2.weight', '2.bias', '4.weight', '4.bias')
ARRAY_NAMES = {'ridge_weights', 'ridge_intercepts', 'x_mean', 'x_scale', 'y_mean', 'y_scale'} | {
    f'n{index}_{name}' for index in range(2) for name in PARAMETERS}


def _digest(arrays, metadata):
    digest = hashlib.sha256(metadata.encode('utf-8'))
    for name in sorted(arrays):
        value = np.ascontiguousarray(arrays[name])
        digest.update(name.encode('ascii'))
        digest.update(value.dtype.str.encode('ascii'))
        digest.update(json.dumps(value.shape).encode('ascii'))
        digest.update(value.tobytes())
    return digest.hexdigest()


def _validate(arrays, metadata):
    if set(arrays) != ARRAY_NAMES or not isinstance(metadata, dict) or set(metadata) != {'format', 'features', 'radius', 'context'}:
        raise ValueError('Unexpected model contents')
    features, radius = metadata['features'], metadata['radius']
    if (metadata['format'] != FORMAT or not isinstance(features, int) or isinstance(features, bool)
            or not 1 <= features <= 4096 or isinstance(radius, bool) or not isinstance(radius, (int, float))
            or not np.isfinite(radius) or radius < 0 or not isinstance(metadata['context'], dict)):
        raise ValueError('Invalid model metadata')
    shapes = {'ridge_weights': (3, features), 'ridge_intercepts': (3,),
              'x_mean': (2, features), 'x_scale': (2, features), 'y_mean': (2,), 'y_scale': (2,)}
    for index in range(2):
        shapes.update({f'n{index}_0.weight': (256, features), f'n{index}_0.bias': (256,),
                       f'n{index}_2.weight': (128, 256), f'n{index}_2.bias': (128,),
                       f'n{index}_4.weight': (1, 128), f'n{index}_4.bias': (1,)})
    if any(arrays[name].shape != shape or arrays[name].dtype.kind != 'f' or not np.isfinite(arrays[name]).all()
           for name, shape in shapes.items()):
        raise ValueError('Invalid model arrays')
    if np.any(arrays['x_scale'] <= 0) or np.any(arrays['y_scale'] <= 0):
        raise ValueError('Invalid model normalization')


def save_hybrid_snapshot(path, models, radius, context):
    if isinstance(radius, bool) or not isinstance(radius, (int, float)) or not np.isfinite(radius) or radius < 0:
        raise ValueError('Invalid model radius')
    if len(models) != 5:
        raise ValueError('Expected three ridge and two neural models')
    arrays = {'ridge_weights': np.stack([np.asarray(model.coef_, dtype=np.float64) for model in models[:3]]),
              'ridge_intercepts': np.asarray([model.intercept_ for model in models[:3]], dtype=np.float64),
              'x_mean': np.stack([model.x_mean for model in models[3:]]),
              'x_scale': np.stack([model.x_scale for model in models[3:]]),
              'y_mean': np.asarray([model.y_mean for model in models[3:]], dtype=np.float64),
              'y_scale': np.asarray([model.y_scale for model in models[3:]], dtype=np.float64)}
    for index, model in enumerate(models[3:]):
        state = model.model.state_dict()
        for name in PARAMETERS:
            arrays[f'n{index}_{name}'] = state[name].detach().cpu().numpy().copy()
    metadata = {'format': FORMAT, 'features': int(arrays['ridge_weights'].shape[1]),
                'radius': float(radius), 'context': context}
    _validate(arrays, metadata)
    encoded = json.dumps(metadata, sort_keys=True, separators=(',', ':'), allow_nan=False)
    fingerprint = _digest(arrays, encoded)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix='.hybrid-', delete=False) as file:
            temporary = Path(file.name)
            np.savez_compressed(file, allow_pickle=False, **arrays, metadata=np.array(encoded),
                                content_sha256=np.array(fingerprint))
            file.flush()
            os.fsync(file.fileno())
        load_hybrid_snapshot(temporary)
        os.link(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


class HybridSnapshot:
    def __init__(self, arrays, metadata):
        self.arrays, self.metadata = arrays, metadata

    def predict(self, representations):
        original = np.asarray(representations)
        if original.dtype.kind not in ('f', 'i', 'u'):
            raise ValueError('Invalid input representations')
        values = np.asarray(original, dtype=np.float64)
        if (values.ndim != 2 or values.shape[0] < 1 or values.shape[1] != self.metadata['features']
                or not np.isfinite(values).all()):
            raise ValueError('Invalid input representations')
        arrays = self.arrays
        members = [values @ weight + intercept for weight, intercept in
                   zip(arrays['ridge_weights'], arrays['ridge_intercepts'])]
        for index in range(2):
            x = (values.astype(np.float32) - arrays['x_mean'][index]) / arrays['x_scale'][index]
            for layer in (0, 2, 4):
                x = x @ arrays[f'n{index}_{layer}.weight'].T + arrays[f'n{index}_{layer}.bias']
                if layer != 4:
                    x = np.maximum(x, 0)
            members.append(x[:, 0].astype(np.float64) * arrays['y_scale'][index] + arrays['y_mean'][index])
        predictions = np.stack(members)
        if not np.isfinite(predictions).all():
            raise ValueError('Nonfinite model output')
        mean, spread = predictions.mean(axis=0), predictions.std(axis=0, ddof=0)
        radius = self.metadata['radius']
        return {'mean': mean, 'spread': spread, 'lower': mean - radius, 'upper': mean + radius}


def load_hybrid_snapshot(path, expected_sha256=None):
    path = Path(path)
    if expected_sha256 is not None and hashlib.sha256(path.read_bytes()).hexdigest() != expected_sha256:
        raise ValueError('Model file fingerprint mismatch')
    with np.load(path, allow_pickle=False) as archive:
        expected = ARRAY_NAMES | {'metadata', 'content_sha256'}
        if set(archive.files) != expected or len(archive.files) != len(expected):
            raise ValueError('Unexpected model archive contents')
        arrays = {name: archive[name].copy() for name in ARRAY_NAMES}
        encoded, fingerprint = archive['metadata'].item(), archive['content_sha256'].item()
    if not isinstance(encoded, str) or not isinstance(fingerprint, str):
        raise ValueError('Invalid model archive metadata')
    metadata = json.loads(encoded)
    _validate(arrays, metadata)
    if _digest(arrays, encoded) != fingerprint:
        raise ValueError('Model content fingerprint mismatch')
    return HybridSnapshot(arrays, metadata)
