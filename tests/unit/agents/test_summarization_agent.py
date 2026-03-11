import pytest
from unittest.mock import AsyncMock

from enterprise_ai_platform.agents.unit.summarization_agent import SummarizationAgent
from enterprise_ai_platform.core.agent_context import AgentContext
from enterprise_ai_platform.models.domain import TaskInput


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
