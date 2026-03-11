from enterprise_ai_platform.api.v1.agents import execute_agent
from enterprise_ai_platform.api.v1.capabilities import list_capabilities
import pytest

from enterprise_ai_platform.api.v1.demo import (
    GraphPreviewRequest,
    WorkflowExecuteRequest,
    demo_graph_preview,
    demo_providers,
    demo_scenarios,
    demo_workflow_execute,
    demo_workflows,
)
from enterprise_ai_platform.api.v1.health import health
from enterprise_ai_platform.dependencies import get_llm_client
from enterprise_ai_platform.dependencies import get_task_service
from enterprise_ai_platform.web_demo import demo_html_response
from enterprise_ai_platform.models.domain import TaskInput


@pytest.mark.asyncio
async def test_execute_agent_endpoint(agent_service) -> None:
    body = await execute_agent(
        TaskInput(capability="summarization", payload={"text": "hello world"}),
        agent_service=agent_service,
    )
    assert body.status == "completed"
    assert body.agent_id == "summarization_agent"


def test_capabilities_endpoint() -> None:
    body = list_capabilities()
    assert "capabilities" in body


def test_demo_endpoints_expose_provider_and_scenarios() -> None:
    provider_body = demo_providers(llm_client=get_llm_client())
    scenarios_body = demo_scenarios()
    workflows_body = demo_workflows()
    health_body = health()

    assert "llm" in provider_body
    assert provider_body["llm"]["provider"]
    assert scenarios_body["scenarios"]
    assert workflows_body["workflows"]
    assert "llm" in health_body


def test_demo_html_response_contains_console() -> None:
    response = demo_html_response()

    assert response.status_code == 200
    assert "단일 작업 실행" in response.body.decode("utf-8")


@pytest.mark.asyncio
async def test_demo_graph_preview_returns_steps() -> None:
    body = await demo_graph_preview(
        GraphPreviewRequest(request="summarize this quarterly update"),
        task_service=get_task_service(),
    )

    assert "steps" in body
    assert isinstance(body["steps"], list)


@pytest.mark.asyncio
async def test_demo_workflow_execute_returns_plan_and_output() -> None:
    body = await demo_workflow_execute(
        WorkflowExecuteRequest(
            request="지난 분기 매출 데이터를 분석하고 경영진용 보고서를 생성해줘",
            payload={"data_source": "quarterly_sales", "quarter": "2025-Q4"},
        ),
        task_service=get_task_service(),
    )

    assert "plan" in body
    assert body["plan"]["steps"]
    assert body["status"] in {"completed", "failed"}
