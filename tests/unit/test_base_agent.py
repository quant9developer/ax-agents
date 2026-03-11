import pytest

from enterprise_ai_platform.core.agent_context import AgentContext
from enterprise_ai_platform.core.base_agent import BaseAgent
from enterprise_ai_platform.core.llm_client import LLMClient
from enterprise_ai_platform.core.tool_manager import ToolManager
from enterprise_ai_platform.knowledge.retriever import Retriever
from enterprise_ai_platform.knowledge.vector_store import VectorStore
from enterprise_ai_platform.models.domain import AgentCategory, AgentMetadata, CapabilityDescriptor, TaskInput, TaskStatus


class DemoAgent(BaseAgent):
    def metadata(self) -> AgentMetadata:
        return AgentMetadata(
            agent_id="demo_agent",
            name="Demo",
            description="Demo",
            category=AgentCategory.DOCUMENT,
            capabilities=[
                CapabilityDescriptor(
                    name="demo",
                    description="Demo",
                    input_schema={"type": "object"},
                    output_schema={"type": "object"},
                    category=AgentCategory.DOCUMENT,
                )
            ],
        )

    async def execute(self, task: TaskInput, context: AgentContext) -> dict[str, object]:
        _ = context
        return {"echo": task.payload}


@pytest.mark.asyncio
async def test_run_success() -> None:
    ctx = AgentContext(llm=LLMClient(), tools=ToolManager(), knowledge=Retriever(VectorStore()))
    result = await DemoAgent().run(TaskInput(capability="demo", payload={"x": 1}), ctx)
    assert result.status == TaskStatus.COMPLETED
    assert result.output == {"echo": {"x": 1}}
