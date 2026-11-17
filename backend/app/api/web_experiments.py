"""Local-only API for bounded retrospective experiments."""
import ipaddress
import logging
import re
from typing import Literal

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.llm.local_advisor import AdvisorConfigurationError
from app.workspace.runs_service import RunBusy, list_experiments, read_experiment, run_experiment
from app.workspace.run_review import review_run
from app.workspace.goals_service import GoalChanged

router = APIRouter()
logger = logging.getLogger(__name__)


class ExperimentRequest(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    seed: int = Field(ge=0, le=2147483647)
    repair: bool = False
    gemini: bool = False
    goal_id: str | None = Field(default=None, pattern='^[0-9a-f]{32}$')
    goal_sha256: str | None = Field(default=None, pattern='^[0-9a-f]{64}$')

    @model_validator(mode='after')
    def check_mode(self):
        if (self.goal_id is None) != (self.goal_sha256 is None):
            raise ValueError('Goal identifier and fingerprint must be supplied together')
        if self.gemini and not self.repair:
            raise ValueError('Gemini requires repair mode')
        return self


def local_only(request):
    try:
        if request.client is None or not ipaddress.ip_address(request.client.host).is_loopback:
            raise ValueError('Non-local client')
    except ValueError as error:
        raise HTTPException(status_code=403, detail='Experiments are available only to local clients.') from error


@router.post('/api/experiments/{dataset}', status_code=201)
def create_experiment(dataset: Literal['amylase', 'ired', 'hydro-P06241', 'hydro-P01053', 'hydro-P0A9X9'],
                      body: ExperimentRequest, request: Request):
    local_only(request)
    try:
        return run_experiment(body.seed, body.repair, body.gemini, dataset, body.goal_id, body.goal_sha256)
    except GoalChanged as error:
        raise HTTPException(status_code=409, detail='Saved goal is missing or has changed.') from error
    except AdvisorConfigurationError as error:
        raise HTTPException(status_code=503, detail='Gemini configuration is unavailable.') from error
    except RunBusy as error:
        raise HTTPException(status_code=409, detail='Another local experiment is running.') from error
    except Exception as error:
        logger.exception('Local experiment failed; partial record may be retained')
        raise HTTPException(status_code=500, detail='Experiment failed; any partial record was retained.') from error


@router.get('/api/experiments')
@router.get('/api/experiments/amylase')
def recent_experiments(request: Request):
    local_only(request)
    return list_experiments()


@router.get('/api/experiments/amylase/{run_id}')
def get_experiment(run_id: str, request: Request):
    local_only(request)
    if not re.fullmatch('[0-9a-f]{32}', run_id):
        raise HTTPException(status_code=404, detail='Completed experiment not found.')
    try:
        return read_experiment(run_id)
    except (OSError, ValueError) as error:
        raise HTTPException(status_code=404, detail='Completed experiment not found.') from error


@router.get('/api/experiments/run/{run_id}/review')
def review_experiment(run_id: str, request: Request):
    local_only(request)
    if not re.fullmatch('[0-9a-f]{32}', run_id):
        raise HTTPException(status_code=404, detail='Completed experiment not found.')
    try:
        return review_run(run_id)
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail='Completed experiment not found.') from error
    except (OSError, ValueError, KeyError, TypeError, IndexError, StopIteration) as error:
        raise HTTPException(status_code=409, detail='Saved experiment could not be verified.') from error
