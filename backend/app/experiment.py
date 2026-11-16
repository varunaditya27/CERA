"""Controlled measurement access for a retrospective amylase run."""
import json
import math
import random
import sys
from pathlib import Path

from app.amylase import load_amylase


class Experiment:
    def __init__(self, data_path, reference_path, log_path, seed, initial_count=100,
                 budget=100, batch_size=10, max_mutations=4):
        if not isinstance(seed, int) or isinstance(seed, bool):
            raise ValueError('Seed must be an integer')
        if any(not isinstance(n, int) or isinstance(n, bool) for n in
               (initial_count, budget, batch_size, max_mutations)):
            raise ValueError('Counts must be integers')
        if initial_count < 1 or budget < 0 or batch_size < 1 or max_mutations < 0:
            raise ValueError('Invalid experiment counts')
        self.__sequences, self.__scores, train, data_hash, reference_hash = load_amylase(
            data_path, reference_path, max_mutations)
        if len(train) < initial_count:
            raise ValueError('Not enough eligible starting candidates')
        initial = random.Random(seed).sample(train, initial_count)
        self.__revealed = {identifier: self.__scores[identifier] for identifier in initial}
        self.__budget = budget
        self.__batch_size = batch_size
        self.__log_path = Path(log_path)
        self.__log = self.__log_path.open('x', encoding='utf-8')
        try:
            self.__write({'event': 'start', 'seed': seed, 'initial_count': initial_count,
                          'budget': budget, 'batch_size': batch_size, 'max_mutations': max_mutations,
                          'data_sha256': data_hash, 'reference_sha256': reference_hash,
                          'python_version': sys.version, 'initial': self.__revealed,
                          'remaining': budget, 'stop_reason': self.stop_reason})
        except Exception:
            self.__log.close()
            raise

    def __write(self, event):
        try:
            self.__log.write(json.dumps(event, allow_nan=False) + '\n')
            self.__log.flush()
        except OSError:
            self.__log.close()
            raise

    @property
    def candidates(self):
        return {identifier: sequence for identifier, sequence in self.__sequences.items()
                if identifier not in self.__revealed}

    @property
    def revealed(self):
        return self.__revealed.copy()

    @property
    def revealed_sequences(self):
        return {identifier: self.__sequences[identifier] for identifier in self.__revealed}

    @property
    def remaining(self):
        return self.__budget

    @property
    def stop_reason(self):
        if self.__budget == 0:
            return 'budget_exhausted'
        if len(self.__revealed) == len(self.__sequences):
            return 'no_candidates'
        return None

    def record_settings(self, settings):
        self.__write({'event': 'method', 'settings': settings})

    def reveal(self, identifiers, predictions=None):
        ids = list(identifiers)
        if (not ids or any(not isinstance(i, str) for i in ids) or len(ids) > self.__batch_size
                or len(ids) > self.__budget or len(set(ids)) != len(ids)
                or any(i not in self.__sequences or i in self.__revealed for i in ids)):
            raise ValueError('Invalid measurement request')
        if predictions is not None:
            if (set(predictions) != set(self.candidates) or any(
                    isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value)
                    for value in predictions.values())):
                raise ValueError('Invalid candidate predictions')
        self.__write({'event': 'selection', 'ids': ids, 'predictions': predictions})
        measured = {identifier: self.__scores[identifier] for identifier in ids}
        remaining = self.__budget - len(ids)
        stop_reason = ('budget_exhausted' if remaining == 0 else
                       'no_candidates' if len(self.__revealed) + len(ids) == len(self.__sequences) else None)
        self.__write({'event': 'reveal', 'measurements': measured, 'remaining': remaining,
                      'stop_reason': stop_reason})
        self.__revealed.update(measured)
        self.__budget = remaining
        return measured.copy()

    def close(self):
        self.__log.close()
