import pytest
from unittest.mock import AsyncMock

from enterprise_ai_platform.agents.unit.summarization_agent import SummarizationAgent
from enterprise_ai_platform.core.agent_context import AgentContext
from enterprise_ai_platform.core.llm_client import LLMClient
from enterprise_ai_platform.core.tool_manager import ToolManager
from enterprise_ai_platform.knowledge.retriever import Retriever
from enterprise_ai_platform.knowledge.vector_store import VectorStore
from enterprise_ai_platform.models.domain import TaskInput
from enterprise_ai_platform.models.domain import ToolDescriptor
from enterprise_ai_platform.tools.base_tool import BaseTool


@pytest.fixture
def mock_context() -> AgentContext:
    ctx = AgentContext(llm=AsyncMock(), tools=AsyncMock(), knowledge=AsyncMock())
    ctx.llm.complete.return_value.content = "Test summary. Point 1. Point 2."
    return ctx


@pytest.mark.asyncio
async def test_summarization_returns_valid_output(mock_context: AgentContext) -> None:
    agent = SummarizationAgent()
    task = TaskInput(capability="summarization", payload={"text": "Long text here..."})
    result = await agent.run(task, mock_context)

    assert result.status == "completed"
    assert result.output is not None
    assert "summary" in result.output
    assert isinstance(result.output["key_points"], list)


class FakeFilesystemMCPTool(BaseTool):
    def descriptor(self) -> ToolDescriptor:
        return ToolDescriptor(
            tool_id="mcp",
            name="Fake MCP",
            description="Test MCP connector",
            input_schema={"type": "object"},
            output_schema={"type": "object"},
            transport="mcp",
        )

    async def invoke(self, input_data: dict[str, object]) -> dict[str, object]:
        assert input_data["server"] == "filesystem"
        assert input_data["tool"] == "read_text"
        return {
            "server": "filesystem",
            "tool": "read_text",
            "result": {
                "path": "/workspace/examples/demo/quarterly_update_ko.txt",
                "content": "국내 사업은 성장했고 수익성 개선이 필요합니다. 다음 분기에는 자동화와 업셀링이 중요합니다.",
            },
            "transport": "mcp",
        }


@pytest.mark.asyncio
async def test_summarization_reads_file_from_filesystem_mcp() -> None:
    tools = ToolManager()
    tools.register(FakeFilesystemMCPTool())
    context = AgentContext(llm=LLMClient(), tools=tools, knowledge=Retriever(VectorStore()))
    task = TaskInput(
        capability="summarization",
        payload={"file_path": "examples/demo/quarterly_update_ko.txt", "max_length": 40},
    )

    result = await SummarizationAgent().run(task, context)

    assert result.status == "completed"
    assert result.output is not None
    assert result.output["source_path"] == "/workspace/examples/demo/quarterly_update_ko.txt"
    assert any(trace.action == "summarization_mcp_filesystem" for trace in result.traces)
