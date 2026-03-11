import pytest

from enterprise_ai_platform.api.v1.tasks import TaskCreateRequest, create_task


@pytest.mark.asyncio
async def test_workflow_lifecycle(task_service) -> None:
    body = await create_task(
        TaskCreateRequest(
            request="Analyze last quarter's sales data and generate an executive report",
            payload={"data_source": "sales_db", "quarter": "Q3-2024"},
        ),
        task_service=task_service,
    )
    assert body["task_id"]
    assert body["plan"]["steps"]
