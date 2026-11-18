"""Fingerprint named application modules independent of their package location."""
import hashlib
from pathlib import Path

APP = Path(__file__).resolve().parents[1]

PILOT_SOURCE_NAMES = ('amylase.py', 'amylase_representations.py', 'experiment.py',
                      'predictor_group.py', 'prediction_intervals.py', 'prediction_pilot.py', 'range_report.py',
                      'representation_cache.py', 'representations.py', 'selection.py', 'warning_checks.py',
                      'reward_distance.py', 'reward_selection.py', 'reward_spec.py', 'repair_coordinator.py',
                      'repair_engine.py', 'repair_menu.py', 'repair_verification.py', 'repair_advisor.py',
                      'gemini_client.py', 'ired.py', 'ired_representations.py', 'sources.py', 'acquisition.py',
                      'local_search.py', 'flip2.py', 'hydro.py', 'hydro_representations.py',
                      'disagreement_targets.py', 'registry.py')


def source_hashes(names):
    result = {}
    for name in names:
        if Path(name).name != name:
            raise ValueError('Invalid source filename')
        matches = list(APP.rglob(name))
        if len(matches) != 1 or not matches[0].is_file():
            raise ValueError(f'Expected one application source for {name}')
        result[name] = hashlib.sha256(matches[0].read_bytes()).hexdigest()
    return result


def validate_recorded_sources(recorded, code_hashes):
    paths = [(Path(path).name, value) for path, value in code_hashes.items()
             if path.startswith('backend/app/') and Path(path).name != '__init__.py']
    available = dict(paths)
    if (len(available) != len(paths) or not isinstance(recorded, dict) or set(recorded) != set(PILOT_SOURCE_NAMES)
            or any(name not in available or recorded[name] != available[name] for name in PILOT_SOURCE_NAMES)):
        raise ValueError('Recorded source fingerprints mismatch')


LEGACY_HINT = ('These records were produced by earlier code, so their recorded fingerprints no longer match. '
               'Run the audit with that code: python3 -m scripts.reporting.legacy_audit [--ref <commit>] <script name> <args> '
               '(see docs/overview/reproducing_results.md).')


class CodeChanged(ValueError):
    pass


def require_recorded_code(*matches):
    if not all(matches):
        raise CodeChanged(LEGACY_HINT)
