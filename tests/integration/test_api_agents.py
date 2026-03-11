from enterprise_ai_platform.api.v1.agents import execute_agent
from enterprise_ai_platform.api.v1.a2a import invoke_a2a, list_a2a_agents
from enterprise_ai_platform.api.v1.capabilities import list_capabilities
import pytest

from enterprise_ai_platform.api.v1.demo import (
    GraphPreviewRequest,
    MCPTestRequest,
    WorkflowExecuteRequest,
    demo_graph_preview,
    demo_mcp_test,
    demo_providers,
    demo_protocols,
    demo_scenarios,
    demo_workflow_execute,
    demo_workflows,
)
from enterprise_ai_platform.core.a2a import A2ARequest
from enterprise_ai_platform.api.v1.health import health
from enterprise_ai_platform.dependencies import get_a2a_service, get_llm_client, get_task_service, get_tool_manager
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


@pytest.mark.asyncio
async def test_demo_endpoints_expose_provider_and_scenarios() -> None:
    provider_body = demo_providers(llm_client=get_llm_client())
    protocol_body = await demo_protocols(tool_manager=get_tool_manager(), a2a_service=get_a2a_service())
    scenarios_body = demo_scenarios()
    workflows_body = demo_workflows()
    health_body = health()

    assert "llm" in provider_body
    assert protocol_body["mcp"]["enabled"] is True
    assert "status" in protocol_body["mcp"]
    assert "configured" in protocol_body["mcp"]["status"]
    assert protocol_body["a2a"]["enabled"] is True
    assert provider_body["llm"]["provider"]
    assert scenarios_body["scenarios"]
    assert any(item["capability"] == "deep_research" for item in scenarios_body["scenarios"])
    assert workflows_body["workflows"]
    assert "llm" in health_body


def test_demo_html_response_contains_console() -> None:
    response = demo_html_response()
    html = response.body.decode("utf-8")

    assert response.status_code == 200
    assert "단일 작업 실행" in html
    assert "리서치 출처" in html
    assert "MCP 테스트 대상" in html


@pytest.mark.asyncio
async def test_demo_graph_preview_returns_steps() -> None:
    body = await demo_graph_preview(
        GraphPreviewRequest(request="summarize this quarterly update"),
        task_service=get_task_service(),
    )

    assert "steps" in body
    assert isinstance(body["steps"], list)


@pytest.mark.asyncio
async def test_demo_mcp_test_returns_status_shape() -> None:
    body = await demo_mcp_test(
        MCPTestRequest(query="ai agents", limit=1),
        tool_manager=get_tool_manager(),
    )

    assert "ok" in body
    assert "status" in body
    assert "configured" in body["status"]


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


@pytest.mark.asyncio
async def test_a2a_invoke_returns_task_result() -> None:
    body = await invoke_a2a(
        A2ARequest(
            sender_agent_id="external",
            receiver_agent_id="translation_agent",
            capability="translation",
            payload={"text": "안녕하세요", "source_language": "ko", "target_language": "en"},
        ),
        a2a_service=get_a2a_service(),
    )

    assert body["agent_id"] == "translation_agent"
    assert body["status"] == "completed"


def test_a2a_agents_endpoint_lists_registered_agents() -> None:
    body = list_a2a_agents(a2a_service=get_a2a_service())

    assert body["agents"]
