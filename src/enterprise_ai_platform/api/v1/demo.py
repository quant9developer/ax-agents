from pydantic import BaseModel
from fastapi import APIRouter, Depends

from enterprise_ai_platform.core.llm_client import LLMClient
from enterprise_ai_platform.dependencies import get_llm_client, get_task_service
from enterprise_ai_platform.services.task_service import TaskService

router = APIRouter(tags=["demo"])

DEMO_SCENARIOS = [
    {
        "id": "summarize_brief",
        "title": "경영진 요약",
        "capability": "summarization",
        "request": {
            "capability": "summarization",
            "payload": {
                "text": (
                    "분기 매출은 전년 대비 18퍼센트 성장했고 영업이익률은 2포인트 개선되었습니다. "
                    "엔터프라이즈 부문이 성장을 이끌었지만 APAC 지역에서는 온보딩 비용이 증가했습니다."
                ),
                "max_length": 80,
                "style": "executive",
            },
        },
    },
    {
        "id": "translate_customer_reply",
        "title": "고객 응답 번역",
        "capability": "translation",
        "request": {
            "capability": "translation",
            "payload": {
                "text": "안녕하세요. 기다려 주셔서 감사합니다. 청구 문제는 해결되었습니다.",
                "source_language": "ko",
                "target_language": "en",
            },
        },
    },
    {
        "id": "generate_report",
        "title": "경영 보고서 생성",
        "capability": "report_generation",
        "request": {
            "capability": "report_generation",
            "payload": {
                "title": "4분기 사업 리뷰",
                "data": {"revenue": 1200000, "growth_rate": 0.18, "retention": 0.94},
                "report_type": "executive",
                "sections": ["개요", "성과", "리스크"],
            },
        },
    },
    {
        "id": "generate_code",
        "title": "코드 생성",
        "capability": "code_generation",
        "request": {
            "capability": "code_generation",
            "payload": {
                "requirement": "이메일 주소를 정규화하는 Python 함수를 작성하세요.",
                "language": "python",
            },
        },
    },
]

DEMO_WORKFLOWS = [
    {
        "id": "sales_analysis_report",
        "title": "매출 분석 후 경영 보고서 생성",
        "request": "지난 분기 매출 데이터를 분석하고 경영진용 보고서를 생성해줘",
        "payload": {
            "data_source": "quarterly_sales",
            "quarter": "2025-Q4",
        },
        "expected_capabilities": [
            "text_to_analytics",
            "statistical_analysis",
            "report_generation",
        ],
    }
]


@router.get("/demo/providers")
def demo_providers(llm_client: LLMClient = Depends(get_llm_client)) -> dict[str, object]:
    return {"llm": llm_client.provider_info()}


@router.get("/demo/scenarios")
def demo_scenarios() -> dict[str, object]:
    return {"scenarios": DEMO_SCENARIOS}


@router.get("/demo/workflows")
def demo_workflows() -> dict[str, object]:
    return {"workflows": DEMO_WORKFLOWS}


class GraphPreviewRequest(BaseModel):
    request: str


@router.post("/demo/graph")
async def demo_graph_preview(
    body: GraphPreviewRequest,
    task_service: TaskService = Depends(get_task_service),
) -> dict[str, object]:
    plan = await task_service.graph.resolve(body.request)
    return {
        "request": body.request,
        "steps": [
            {
                "step_number": step.step_number,
                "capability": step.capability,
                "depends_on": step.depends_on,
                "input_mapping": step.input_mapping,
            }
            for step in plan.steps
        ],
    }


class WorkflowExecuteRequest(BaseModel):
    request: str
    payload: dict[str, object] = {}


@router.post("/demo/workflows/execute")
async def demo_workflow_execute(
    body: WorkflowExecuteRequest,
    task_service: TaskService = Depends(get_task_service),
) -> dict[str, object]:
    plan, result = await task_service.create_task(body.request, body.payload)
    return {
        "task_id": result.task_id,
        "status": result.status,
        "agent_id": result.agent_id,
        "plan": {
            "steps": [
                {
                    "step_number": step.step_number,
                    "capability": step.capability,
                    "depends_on": step.depends_on,
                    "input_mapping": step.input_mapping,
                }
                for step in plan.steps
            ]
        },
        "output": result.output,
        "error": result.error.model_dump() if result.error is not None else None,
        "traces": [trace.model_dump() for trace in result.traces],
        "duration_ms": result.duration_ms,
    }
