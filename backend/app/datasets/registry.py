"""Resolve supported protein datasets to their source files and loader."""
from app.datasets import amylase, hydro, ired


def dataset_source(dataset):
    if dataset == 'amylase':
        return amylase.DATA, amylase.REFERENCE, amylase.load_amylase
    if dataset == 'ired':
        return ired.DATA, ired.REFERENCE, amylase.load_amylase
    if isinstance(dataset, str) and dataset.startswith('hydro-') and dataset[6:] in hydro.PROTEINS:
        return hydro.DATA, hydro.REFERENCES[dataset[6:]], hydro.load_hydro
    raise ValueError('Unknown dataset')
