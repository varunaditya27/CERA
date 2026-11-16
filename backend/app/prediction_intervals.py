"""Compute initial split-conformal ranges and report observed coverage."""
import math

import numpy as np


def interval_radius(predictions, scores, miscoverage=0.1):
    predictions = np.asarray(predictions, dtype=np.float64)
    scores = np.asarray(scores, dtype=np.float64)
    if (predictions.ndim != 1 or not predictions.size or predictions.shape != scores.shape
            or not np.isfinite(predictions).all() or not np.isfinite(scores).all()
            or not 0 < miscoverage < 1):
        raise ValueError('Invalid range-setting data')
    rank = math.ceil((len(scores) + 1) * (1 - miscoverage))
    if rank > len(scores):
        raise ValueError('Too few range-setting examples for a finite interval')
    errors = np.abs(scores - predictions)
    return float(np.partition(errors, rank - 1)[rank - 1])


def batch_coverage(ranges, measurements):
    if not measurements or not set(measurements).issubset(ranges):
        raise ValueError('Missing measured prediction ranges')
    covered, widths = 0, []
    for identifier, score in measurements.items():
        lower, upper = ranges[identifier]['lower'], ranges[identifier]['upper']
        if not all(math.isfinite(x) for x in (lower, upper, score)) or lower > upper:
            raise ValueError('Invalid measurement or bounds')
        covered += lower <= score <= upper
        widths.append(upper - lower)
    return covered, len(widths), sum(widths)
