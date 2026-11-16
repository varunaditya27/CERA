"""Fit a bootstrap group after selecting model settings on unique examples."""
import numpy as np
from sklearn.linear_model import Ridge, RidgeCV
from sklearn.model_selection import KFold

from app.selection import PENALTIES


def fit_group(vectors, scores, fitting_ids, reserved_ids, cv_seed, member_seeds):
    ids = sorted(fitting_ids)
    if (len(ids) < 5 or len(ids) != len(set(ids)) or set(ids) & set(reserved_ids)
            or len(member_seeds) != 5 or len(set(member_seeds)) != 5):
        raise ValueError('Invalid fitting, reserved or member identifiers')
    x = np.asarray([vectors[identifier] for identifier in ids], dtype=np.float64)
    y = np.asarray([scores[identifier] for identifier in ids], dtype=np.float64)
    if x.ndim != 2 or y.shape != (len(ids),) or not np.isfinite(x).all() or not np.isfinite(y).all():
        raise ValueError('Invalid fitting data')
    cv = KFold(n_splits=5, shuffle=True, random_state=cv_seed)
    penalty = float(RidgeCV(alphas=PENALTIES, cv=cv, scoring='neg_mean_squared_error').fit(x, y).alpha_)
    models = []
    for seed in member_seeds:
        indices = np.random.default_rng(seed).integers(0, len(ids), size=len(ids))
        models.append(Ridge(alpha=penalty).fit(x[indices], y[indices]))
    return models, penalty


def predict_group(models, vectors, identifiers):
    ids = list(identifiers)
    if len(models) != 5 or not ids or len(ids) != len(set(ids)):
        raise ValueError('Invalid predictor group or candidate identifiers')
    x = np.asarray([vectors[identifier] for identifier in ids], dtype=np.float64)
    if x.ndim != 2 or not np.isfinite(x).all():
        raise ValueError('Invalid candidate representations')
    predictions = np.asarray([model.predict(x) for model in models])
    if predictions.shape != (5, len(ids)) or not np.isfinite(predictions).all():
        raise ValueError('Invalid model predictions')
    return predictions.mean(axis=0), predictions.std(axis=0, ddof=0)
