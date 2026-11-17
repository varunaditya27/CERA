"""Fit an opt-in group of ridge and neural predictors on revealed examples."""
import copy
import math
import random

import numpy as np
import torch
from torch import nn

from app.experiments.predictor_group import fit_group

MAX_EPOCHS = 200
PATIENCE = 20
LEARNING_RATE = 0.001
WEIGHT_DECAY = 0.0001


def hybrid_configuration(device):
    if device not in ('cpu', 'cuda') or (device == 'cuda' and not torch.cuda.is_available()):
        raise ValueError('Requested neural-network device is unavailable')
    return {'device': device, 'gpu': torch.cuda.get_device_name() if device == 'cuda' else None,
            'torch': str(torch.__version__), 'cuda_build': torch.version.cuda,
            'ridge_members': 3, 'neural_members': 2, 'hidden_units': [256, 128],
            'validation_fraction': .2, 'learning_rate': LEARNING_RATE, 'weight_decay': WEIGHT_DECAY,
            'max_epochs': MAX_EPOCHS, 'patience': PATIENCE, 'batch': 'full'}


class NeuralPredictor:
    def __init__(self, model, x_mean, x_scale, y_mean, y_scale, device):
        self.model, self.device = model, device
        self.x_mean, self.x_scale = x_mean, x_scale
        self.y_mean, self.y_scale = y_mean, y_scale

    def predict(self, values):
        array = (np.asarray(values, dtype=np.float32) - self.x_mean) / self.x_scale
        with torch.inference_mode():
            output = self.model(torch.as_tensor(array, dtype=torch.float32, device=self.device)).flatten()
        return output.cpu().numpy().astype(np.float64) * self.y_scale + self.y_mean


def fit_hybrid_group(vectors, scores, fitting_ids, reserved_ids, cv_seed, member_seeds, device='cuda'):
    ids = sorted(fitting_ids)
    hybrid_configuration(device)
    if (len(ids) < 10 or len(ids) != len(set(ids)) or set(ids) & set(reserved_ids)
            or len(member_seeds) != 5 or len(set(member_seeds)) != 5):
        raise ValueError('Invalid hybrid predictor roles or seeds')
    validation = sorted(random.Random(cv_seed).sample(ids, math.ceil(len(ids) * .2)))
    training = sorted(set(ids) - set(validation))
    x_train = np.asarray([vectors[i] for i in training], dtype=np.float32)
    y_train = np.asarray([scores[i] for i in training], dtype=np.float32)
    x_validation = np.asarray([vectors[i] for i in validation], dtype=np.float32)
    y_validation = np.asarray([scores[i] for i in validation], dtype=np.float32)
    if (x_train.ndim != 2 or x_validation.shape != (len(validation), x_train.shape[1])
            or not all(np.isfinite(a).all() for a in (x_train, y_train, x_validation, y_validation))):
        raise ValueError('Invalid hybrid predictor data')
    x_mean, x_scale = x_train.mean(axis=0), x_train.std(axis=0)
    x_scale = np.where(x_scale < 1e-12, 1.0, x_scale).astype(np.float32)
    y_mean, y_scale = float(y_train.mean()), float(y_train.std())
    if y_scale < 1e-12:
        y_scale = 1.0
    train_x = torch.as_tensor((x_train - x_mean) / x_scale, dtype=torch.float32, device=device)
    train_y = torch.as_tensor((y_train - y_mean) / y_scale, dtype=torch.float32, device=device)
    val_x = torch.as_tensor((x_validation - x_mean) / x_scale, dtype=torch.float32, device=device)
    val_y = torch.as_tensor((y_validation - y_mean) / y_scale, dtype=torch.float32, device=device)
    models, penalty = fit_group(vectors, scores, ids, reserved_ids, cv_seed, member_seeds, ridge_members=3)
    metadata = []
    for seed in member_seeds[3:]:
        sample = np.random.default_rng(seed).integers(0, len(training), size=len(training))
        indices = torch.as_tensor(sample, device=device)
        with torch.random.fork_rng(devices=[]):
            torch.random.default_generator.manual_seed(seed)
            network = nn.Sequential(nn.Linear(x_train.shape[1], 256, device='cpu'), nn.ReLU(),
                                    nn.Linear(256, 128, device='cpu'), nn.ReLU(),
                                    nn.Linear(128, 1, device='cpu')).to(device)
            optimizer = torch.optim.Adam(network.parameters(), lr=LEARNING_RATE, weight_decay=WEIGHT_DECAY)
            best_loss, best_epoch, best_state, stale = float('inf'), 0, None, 0
            for epoch in range(1, MAX_EPOCHS + 1):
                network.train()
                optimizer.zero_grad(set_to_none=True)
                loss = nn.functional.mse_loss(network(train_x[indices]).flatten(), train_y[indices])
                if not torch.isfinite(loss):
                    raise ValueError('Nonfinite neural training loss')
                loss.backward()
                optimizer.step()
                network.eval()
                with torch.inference_mode():
                    validation_loss = float(nn.functional.mse_loss(network(val_x).flatten(), val_y).item())
                if not math.isfinite(validation_loss):
                    raise ValueError('Nonfinite neural validation loss')
                if validation_loss < best_loss:
                    best_loss, best_epoch, best_state, stale = validation_loss, epoch, copy.deepcopy(network.state_dict()), 0
                else:
                    stale += 1
                    if stale >= PATIENCE:
                        break
            network.load_state_dict(best_state)
            network.eval()
        models.append(NeuralPredictor(network, x_mean, x_scale, y_mean, y_scale, device))
        metadata.append({'seed': seed, 'epochs': epoch, 'best_epoch': best_epoch,
                         'best_validation_mse_normalized': best_loss})
    return models, penalty, {'training_ids': training, 'validation_ids': validation, 'members': metadata}
