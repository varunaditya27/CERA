"""Local-only API for bounded retrospective experiments."""
import ipaddress
import logging
import re

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field

from app.workspace.runs_service import RunBusy, list_experiments, read_experiment, run_experiment

router = APIRouter()
logger = logging.getLogger(__name__)


class ExperimentRequest(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    seed: int = Field(ge=0, le=2147483647)
    repair: bool = False


def local_only(request):
    try:
        if request.client is None or not ipaddress.ip_address(request.client.host).is_loopback:
            raise ValueError('Non-local client')
    except ValueError as error:
        raise HTTPException(status_code=403, detail='Experiments are available only to local clients.') from error


@router.post('/api/experiments/amylase', status_code=201)
def create_experiment(body: ExperimentRequest, request: Request):
    local_only(request)
    try:
        return run_experiment(body.seed, body.repair)
    except RunBusy as error:
        raise HTTPException(status_code=409, detail='Another local experiment is running.') from error
    except Exception as error:
        logger.exception('Local experiment failed; partial record may be retained')
        raise HTTPException(status_code=500, detail='Experiment failed; any partial record was retained.') from error


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
