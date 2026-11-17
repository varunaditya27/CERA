"""Validate the approved four-protein study and cross-group provenance."""
from app.experiments.repeated_runs import METHODS

DATASETS = {'ired', 'hydro-P06241', 'hydro-P01053', 'hydro-P0A9X9'}
SPECIFICATION_SHA256 = '0c94c3eb15d681b2244b388c281e5d30e1954164c2eda970f640a60d378b03a1'


def validate_manifests(manifests, partial_development=False):
    datasets = {manifest['dataset'] for manifest in manifests}
    if not manifests or len(datasets) != len(manifests):
        raise ValueError('Missing or duplicate protein group')
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
