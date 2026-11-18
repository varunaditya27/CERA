"""Configure the existing bounded repair advisor from local settings."""
import os
import re

from app.datasets.amylase import ROOT
from app.llm.gemini_client import request_repair
from app.llm.repair_trace import traced_repair_advice


class AdvisorConfigurationError(Exception):
    pass


def local_gemini_configuration():
    try:
        from dotenv import dotenv_values
    except ImportError as error:
        raise AdvisorConfigurationError('Gemini configuration unavailable') from error
    settings = dotenv_values(ROOT / 'backend/.env')
    key = os.environ.get('GEMINI_API_KEY') or settings.get('GEMINI_API_KEY')
    model = os.environ.get('GEMINI_MODEL') or settings.get('GEMINI_MODEL')
    if not isinstance(key, str) or not key.strip() or not isinstance(model, str) or not re.fullmatch(r'[A-Za-z0-9._-]+', model):
        raise AdvisorConfigurationError('Gemini configuration unavailable')

    return key, model


def local_repair_advisor():
    key, model = local_gemini_configuration()

    def advisor(kind, menu):
        return traced_repair_advice(lambda warning, options: request_repair(key, model, warning, options), kind, menu)

    return advisor, model
