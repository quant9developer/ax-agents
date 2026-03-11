import pytest

from enterprise_ai_platform.agents.unit.document_drafting_agent import DocumentDraftingAgent
from enterprise_ai_platform.agents.unit.report_generation_agent import ReportGenerationAgent
from enterprise_ai_platform.agents.unit.text_to_analytics_agent import TextToAnalyticsAgent
from enterprise_ai_platform.core.agent_context import AgentContext
from enterprise_ai_platform.core.llm_client import LLMClient
from enterprise_ai_platform.core.tool_manager import ToolManager
from enterprise_ai_platform.knowledge.retriever import Retriever
from enterprise_ai_platform.knowledge.vector_store import VectorStore
from enterprise_ai_platform.models.domain import TaskInput


def build_context() -> AgentContext:
    return AgentContext(llm=LLMClient(), tools=ToolManager(), knowledge=Retriever(VectorStore()))


@pytest.mark.asyncio
async def test_document_drafting_korean_fallback() -> None:
    result = await DocumentDraftingAgent().run(
        TaskInput(
            capability="document_drafting",
            payload={
                "document_type": "보고서",
                "topic": "국내 유통 산업의 AI 전환 전략",
                "outline": ["배경", "핵심 과제", "권고안"],
            },
        ),
        build_context(),
    )

    assert result.status == "completed"
    assert result.output is not None
    assert "AI 전환 전략" in result.output["title"]
    assert "초안 수준의 작업 문서" in result.output["sections"][0]["content"]


@pytest.mark.asyncio
async def test_report_generation_korean_fallback() -> None:
    result = await ReportGenerationAgent().run(
        TaskInput(
            capability="report_generation",
            payload={
                "title": "4분기 사업 리뷰",
                "data": {"매출": 1200000, "성장률": 0.18},
                "sections": ["개요", "성과"],
            },
        ),
        build_context(),
    )

    assert result.status == "completed"
    assert result.output is not None
    assert "요약합니다" in result.output["executive_summary"]
    assert "데이터 필드" in result.output["sections"][0]["content"]


@pytest.mark.asyncio
async def test_text_to_analytics_korean_fallback() -> None:
    result = await TextToAnalyticsAgent().run(
        TaskInput(
            capability="text_to_analytics",
            payload={
                "question": "지난 분기 지역별 매출 상위 5개를 보여줘",
                "data_source": "quarterly_sales",
            },
        ),
        build_context(),
    )

    assert result.status == "completed"
    assert result.output is not None
    assert "읽기 전용 SQL 템플릿" in result.output["result_summary"]
