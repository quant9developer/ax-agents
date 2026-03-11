import pytest

from enterprise_ai_platform.agents.unit.deep_research_agent import DeepResearchAgent
from enterprise_ai_platform.core.agent_context import AgentContext
from enterprise_ai_platform.core.llm_client import LLMClient
from enterprise_ai_platform.core.tool_manager import ToolManager
from enterprise_ai_platform.knowledge.retriever import Retriever
from enterprise_ai_platform.knowledge.vector_store import VectorStore
from enterprise_ai_platform.models.domain import TaskInput, ToolDescriptor
from enterprise_ai_platform.tools.base_tool import BaseTool


class FakeMCPTool(BaseTool):
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
        assert input_data["server"] == "browser"
        assert input_data["tool"] == "search"
        assert input_data["arguments"]["query"] in {"enterprise ai agents", "한국 리테일 산업의 AI 에이전트 도입 사례"}
        return {
            "server": "browser",
            "tool": "search",
            "result": {
                "items": [
                    {
                        "title": "AI agent market update",
                        "snippet": "The enterprise AI agent market continues to expand in regulated industries.",
                        "url": "https://example.com/market-update",
                    }
                ]
            },
            "transport": "mcp",
        }


class FakeMCPToolWithoutSnippet(BaseTool):
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
        _ = input_data
        return {
            "server": "browser",
            "tool": "search",
            "result": {
                "items": [
                    {
                        "title": "한국 Ai 에이전트 사례 정리",
                        "snippet": "",
                        "url": "https://example.com/korean-ai-agents",
                    }
                ]
            },
            "transport": "mcp",
        }


@pytest.mark.asyncio
async def test_deep_research_uses_mcp_browser_results() -> None:
    tools = ToolManager()
    tools.register(FakeMCPTool())
    context = AgentContext(llm=LLMClient(), tools=tools, knowledge=Retriever(VectorStore()))
    task = TaskInput(
        capability="deep_research",
        payload={"topic": "enterprise ai agents", "depth": "comprehensive", "sources_limit": 3},
    )

    result = await DeepResearchAgent().run(task, context)

    assert result.status == "completed"
    assert result.output is not None
    assert result.output["supporting_evidence"][0]["source"] == "https://example.com/market-update"
    assert result.output["sources"][0]["url"] == "https://example.com/market-update"
    assert result.output["sources"][0]["title"] == "AI agent market update"
    assert any(trace.action == "deep_research_mcp" for trace in result.traces)


@pytest.mark.asyncio
async def test_deep_research_uses_plain_korean_topic_as_mcp_query() -> None:
    tools = ToolManager()
    tools.register(FakeMCPTool())
    context = AgentContext(llm=LLMClient(), tools=tools, knowledge=Retriever(VectorStore()))
    task = TaskInput(
        capability="deep_research",
        payload={"topic": "한국 리테일 산업의 AI 에이전트 도입 사례", "depth": "comprehensive", "sources_limit": 3},
    )

    result = await DeepResearchAgent().run(task, context)

    assert result.status == "completed"
    assert result.output is not None
    assert result.output["sources"]


@pytest.mark.asyncio
async def test_deep_research_keeps_mcp_results_even_without_snippet() -> None:
    tools = ToolManager()
    tools.register(FakeMCPToolWithoutSnippet())
    context = AgentContext(llm=LLMClient(), tools=tools, knowledge=Retriever(VectorStore()))
    task = TaskInput(
        capability="deep_research",
        payload={"topic": "한국 리테일 산업의 AI 에이전트 도입 사례", "depth": "comprehensive", "sources_limit": 3},
    )

    result = await DeepResearchAgent().run(task, context)

    assert result.status == "completed"
    assert result.output is not None
    assert result.output["sources"][0]["url"] == "https://example.com/korean-ai-agents"
    assert result.output["supporting_evidence"]
    assert any(trace.action == "deep_research_mcp" for trace in result.traces)


@pytest.mark.asyncio
async def test_deep_research_falls_back_without_mcp() -> None:
    context = AgentContext(llm=LLMClient(), tools=ToolManager(), knowledge=Retriever(VectorStore()))
    task = TaskInput(
        capability="deep_research",
        payload={"topic": "korean retail analytics", "depth": "standard", "sources_limit": 2},
    )

    result = await DeepResearchAgent().run(task, context)

    assert result.status == "completed"
    assert result.output is not None
    assert result.output["summary"]
    assert result.output["supporting_evidence"]
    assert "sources" in result.output


@pytest.mark.asyncio
async def test_deep_research_korean_topic_returns_korean_fallback() -> None:
    context = AgentContext(llm=LLMClient(), tools=ToolManager(), knowledge=Retriever(VectorStore()))
    task = TaskInput(
        capability="deep_research",
        payload={"topic": "한국 리테일 산업의 AI 에이전트 도입 사례", "depth": "standard", "sources_limit": 2},
    )

    result = await DeepResearchAgent().run(task, context)

    assert result.status == "completed"
    assert result.output is not None
    assert "한국" in result.output["summary"]
    assert any(("관련이 있습니다" in item["claim"]) or ("기본 리서치" in item["claim"]) for item in result.output["supporting_evidence"])
    assert "sources" in result.output
