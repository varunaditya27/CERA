"""Local-only endpoints for compiling and reviewing fitness goals."""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field

from app.api.web_experiments import local_only
from app.llm.gemini_client import GeminiError
from app.llm.local_advisor import AdvisorConfigurationError
from app.llm.natural_goal import UnsupportedGoal
from app.workspace.goals_service import compile_and_save, list_goals

router = APIRouter()


class GoalRequest(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    goal: str = Field(min_length=1, max_length=1000)


@router.post('/api/goals', status_code=201)
def compile_goal(body: GoalRequest, request: Request):
    local_only(request)
    if not body.goal.strip():
        raise HTTPException(status_code=422, detail='Enter a goal.')
    try:
        return compile_and_save(body.goal)
    except UnsupportedGoal as error:
        raise HTTPException(status_code=422, detail='This goal is outside the supported fitness search.') from error
    except AdvisorConfigurationError as error:
        raise HTTPException(status_code=503, detail='Gemini configuration is unavailable.') from error
    except (GeminiError, ValueError) as error:
        raise HTTPException(status_code=502, detail='Gemini could not produce a valid goal specification.') from error


@router.get('/api/goals')
def recent_goals(request: Request):
    local_only(request)
    return list_goals()
