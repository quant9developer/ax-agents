import pytest

from enterprise_ai_platform.agents.unit.code_refactor_agent import CodeRefactorAgent
from enterprise_ai_platform.core.agent_context import AgentContext
from enterprise_ai_platform.core.llm_client import LLMClient
from enterprise_ai_platform.core.tool_manager import ToolManager
from enterprise_ai_platform.knowledge.retriever import Retriever
from enterprise_ai_platform.knowledge.vector_store import VectorStore
from enterprise_ai_platform.models.domain import TaskInput


@pytest.mark.asyncio
async def test_code_refactor_returns_korean_explanation_for_korean_request() -> None:
    context = AgentContext(llm=LLMClient(), tools=ToolManager(), knowledge=Retriever(VectorStore()))
    task = TaskInput(
        capability="code_refactor",
        payload={
            "code": "print('hello')\nif value == None:\n    print(value)\n",
            "action": "리팩터링",
            "output_language": "ko",
        },
    )

    result = await CodeRefactorAgent().run(task, context)

    assert result.status == "completed"
    assert result.output is not None
    assert "작업을 수행했습니다" in result.output["explanation"]
    assert any("로깅" in item["description"] or "명확" in item["description"] for item in result.output["improvements"])
