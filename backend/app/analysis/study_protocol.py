"""Validate the approved four-protein study and cross-group provenance."""
from app.experiments.repeated_runs import METHODS

DATASETS = {'ired', 'hydro-P06241', 'hydro-P01053', 'hydro-P0A9X9'}
SPECIFICATION_SHA256 = '0c94c3eb15d681b2244b388c281e5d30e1954164c2eda970f640a60d378b03a1'


def validate_low_change_pool(sequences, train, reference):
    if (len(train) < 100 or len(train) != len(set(train)) or not set(train).issubset(sequences)
            or any(len(sequences[i]) != len(reference) or
                   sum(a != b for a, b in zip(sequences[i], reference)) > 2 for i in train)):
        raise ValueError('IRED train pool is not a valid low-change starting pool')


def validate_ired_low_change(manifests):
    if len(manifests) != 1:
        raise ValueError('IRED low-change study requires exactly one group')
    manifest = manifests[0]
    if (manifest['dataset'] != 'ired' or manifest['initial_pool'] != 'train'
            or manifest['seeds'] != list(range(61, 71)) or manifest['methods'] != list(METHODS)
            or manifest['targeted_disagreement'] is not True or manifest['direct_diversity'] is not True
            or not manifest['gemini_model'] or manifest['specification_sha256'] != SPECIFICATION_SHA256):
        raise ValueError('IRED low-change settings do not match the approved protocol')


def validate_hydro_low_fitness(manifests):
    datasets = {'hydro-P06241', 'hydro-P01053', 'hydro-P0A9X9'}
    if len(manifests) != 3 or {m['dataset'] for m in manifests} != datasets:
        raise ValueError('Hydro low-fitness study requires all three protein groups')
    for manifest in manifests:
        if (manifest['initial_pool'] != 'train' or manifest['seeds'] != list(range(141, 151))
                or manifest['methods'] != list(METHODS) or manifest['targeted_disagreement'] is not True
                or manifest['direct_diversity'] is not True or not manifest['gemini_model']
                or manifest['specification_sha256'] != SPECIFICATION_SHA256):
            raise ValueError('Hydro low-fitness settings do not match the study protocol')
    keys = ('seeds', 'methods', 'targeted_disagreement', 'direct_diversity', 'specification_sha256',
            'code_sha256', 'python', 'versions', 'gemini_model')
    if any(any(m[key] != manifests[0][key] for key in keys) for m in manifests[1:]):
        raise ValueError('Hydro comparison settings differ')


def validate_manifests(manifests, partial_development=False):
    datasets = {manifest['dataset'] for manifest in manifests}
    if not manifests or len(datasets) != len(manifests):
        raise ValueError('Missing or duplicate protein group')
    if any(manifest['initial_pool'] != 'eligible' for manifest in manifests):
        raise ValueError('Matched protein comparison requires eligible starting pools')
    if not partial_development:
        if datasets != DATASETS:
            raise ValueError('Full evaluation requires all four protein groups')
        for manifest in manifests:
            if (manifest['seeds'] != list(range(51, 61)) or manifest['methods'] != list(METHODS)
                    or manifest['targeted_disagreement'] is not True or manifest['direct_diversity'] is not True
                    or not manifest['gemini_model'] or manifest['specification_sha256'] != SPECIFICATION_SHA256):
                raise ValueError('Study scope does not match the approved protocol')
    keys = ('seeds', 'methods', 'targeted_disagreement', 'direct_diversity', 'specification_sha256',
            'code_sha256', 'python', 'versions', 'gemini_model')
    first = manifests[0]
    if any(any(manifest[key] != first[key] for key in keys) for manifest in manifests[1:]):
        raise ValueError('Protein group comparison settings differ')
