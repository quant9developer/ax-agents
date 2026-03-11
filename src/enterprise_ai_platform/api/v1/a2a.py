from fastapi import APIRouter, Depends

from enterprise_ai_platform.core.a2a import A2ARequest, A2AService
from enterprise_ai_platform.dependencies import get_a2a_service

router = APIRouter(tags=["a2a"])


@router.get("/a2a/agents")
def list_a2a_agents(a2a_service: A2AService = Depends(get_a2a_service)) -> dict[str, object]:
    return {"agents": a2a_service.list_agents()}


@router.post("/a2a/invoke")
async def invoke_a2a(
    body: A2ARequest,
    a2a_service: A2AService = Depends(get_a2a_service),
) -> dict[str, object]:
    result = await a2a_service.invoke(body)
    return result.model_dump()
