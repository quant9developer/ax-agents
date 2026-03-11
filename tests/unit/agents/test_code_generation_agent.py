import pytest

from enterprise_ai_platform.agents.unit.code_generation_agent import CodeGenerationAgent
from enterprise_ai_platform.core.agent_context import AgentContext
from enterprise_ai_platform.core.llm_client import LLMClient
from enterprise_ai_platform.core.tool_manager import ToolManager
from enterprise_ai_platform.knowledge.retriever import Retriever
from enterprise_ai_platform.knowledge.vector_store import VectorStore
from enterprise_ai_platform.models.domain import TaskInput


@pytest.mark.asyncio
async def test_code_generation_returns_python_snippet() -> None:
    context = AgentContext(llm=LLMClient(), tools=ToolManager(), knowledge=Retriever(VectorStore()))
    task = TaskInput(
        capability="code_generation",
        payload={"requirement": "return a greeting", "language": "python"},
    )

    result = await CodeGenerationAgent().run(task, context)

    assert result.status == "completed"
    assert result.output is not None
    assert "def generated_solution" in result.output["code"]


@pytest.mark.asyncio
async def test_code_generation_returns_korean_explanation_for_korean_requirement() -> None:
    context = AgentContext(llm=LLMClient(), tools=ToolManager(), knowledge=Retriever(VectorStore()))
    task = TaskInput(
        capability="code_generation",
        payload={"requirement": "이메일 주소를 정규화하는 Python 함수를 작성하세요.", "language": "python"},
    )

    result = await CodeGenerationAgent().run(task, context)

    assert result.status == "completed"
    assert result.output is not None
    assert "구현을 생성했습니다" in result.output["explanation"]
