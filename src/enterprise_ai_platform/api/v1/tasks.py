from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends

from enterprise_ai_platform.dependencies import get_task_service
from enterprise_ai_platform.services.task_service import TaskService

router = APIRouter(tags=["tasks"])


class TaskCreateRequest(BaseModel):
    request: str
    payload: dict[str, object] = Field(default_factory=dict)


@router.post("/tasks", status_code=202)
async def create_task(
    body: TaskCreateRequest,
    task_service: TaskService = Depends(get_task_service),
) -> dict[str, object]:
    plan, result = await task_service.create_task(body.request, body.payload)
    return {
        "task_id": result.task_id,
        "status": result.status,
        "plan": {
            "steps": [
                {
                    "step_number": step.step_number,
                    "capability": step.capability,
                    "depends_on": step.depends_on,
                }
                for step in plan.steps
            ]
        },
    }
