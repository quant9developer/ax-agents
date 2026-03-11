import pytest

from enterprise_ai_platform.agents.unit.table_analysis_agent import TableAnalysisAgent
from enterprise_ai_platform.core.agent_context import AgentContext
from enterprise_ai_platform.core.llm_client import LLMClient
from enterprise_ai_platform.core.tool_manager import ToolManager
from enterprise_ai_platform.knowledge.retriever import Retriever
from enterprise_ai_platform.knowledge.vector_store import VectorStore
from enterprise_ai_platform.models.domain import TaskInput


@pytest.mark.asyncio
async def test_table_analysis_generates_statistics() -> None:
    context = AgentContext(llm=LLMClient(), tools=ToolManager(), knowledge=Retriever(VectorStore()))
    task = TaskInput(
        capability="table_analysis",
        payload={"data": [{"sales": 10, "cost": 4}, {"sales": 20, "cost": 7}, {"sales": 30, "cost": 9}]},
    )

    result = await TableAnalysisAgent().run(task, context)

    assert result.status == "completed"
    assert result.output is not None
    assert "sales" in result.output["statistics"]
    assert result.output["statistics"]["sales"]["mean"] == 20.0
