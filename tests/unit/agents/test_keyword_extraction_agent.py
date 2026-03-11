import pytest

from enterprise_ai_platform.agents.unit.keyword_extraction_agent import KeywordExtractionAgent
from enterprise_ai_platform.core.agent_context import AgentContext
from enterprise_ai_platform.core.llm_client import LLMClient
from enterprise_ai_platform.core.tool_manager import ToolManager
from enterprise_ai_platform.knowledge.retriever import Retriever
from enterprise_ai_platform.knowledge.vector_store import VectorStore
from enterprise_ai_platform.models.domain import TaskInput


@pytest.mark.asyncio
async def test_keyword_extraction_returns_keywords_and_entities() -> None:
    context = AgentContext(llm=LLMClient(), tools=ToolManager(), knowledge=Retriever(VectorStore()))
    task = TaskInput(
        capability="keyword_extraction",
        payload={"text": "OpenAI built ChatGPT in San Francisco for enterprise AI operations."},
    )

    result = await KeywordExtractionAgent().run(task, context)

    assert result.status == "completed"
    assert result.output is not None
    assert result.output["keywords"]
    assert isinstance(result.output["entities"], list)
