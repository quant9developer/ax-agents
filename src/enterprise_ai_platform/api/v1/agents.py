from fastapi import APIRouter, Depends, HTTPException

from enterprise_ai_platform.dependencies import get_agent_service
from enterprise_ai_platform.models.domain import TaskInput, TaskResult
from enterprise_ai_platform.services.agent_service import AgentService

router = APIRouter(tags=["agents"])


@router.post("/agents/execute", response_model=TaskResult)
async def execute_agent(
    task_input: TaskInput,
    agent_service: AgentService = Depends(get_agent_service),
) -> TaskResult:
    try:
        return await agent_service.execute(task_input)
    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail={
                "error": {
                    "code": "CAPABILITY_NOT_FOUND",
                    "message": str(exc),
                    "retryable": False,
                }
            },
        ) from exc
