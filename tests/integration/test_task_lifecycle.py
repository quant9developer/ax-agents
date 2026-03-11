import pytest

from enterprise_ai_platform.api.v1.tasks import TaskCreateRequest, create_task


@pytest.mark.asyncio
async def test_create_task(task_service) -> None:
    body = await create_task(
        TaskCreateRequest(request="summarize this text", payload={}),
        task_service=task_service,
    )
    assert body["status"] in {"completed", "pending"}
