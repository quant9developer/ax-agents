from __future__ import annotations

from dataclasses import dataclass, field

from enterprise_ai_platform.core.capability_registry import CapabilityRegistry
from enterprise_ai_platform.core.llm_client import LLMClient


@dataclass
class ExecutionStep:
    step_number: int
    capability: str
    input_mapping: dict[str, str]
    depends_on: list[int] = field(default_factory=list)


@dataclass
class ExecutionPlan:
    steps: list[ExecutionStep]
    original_request: str


class CapabilityGraph:
    def __init__(self, registry: type[CapabilityRegistry], llm: LLMClient):
        self.registry = registry
        self.llm = llm

    async def resolve(self, request: str) -> ExecutionPlan:
        lower = request.lower()
        available = self.registry.list_capabilities()

        is_report_request = any(token in lower for token in ["report", "보고서"])
        is_analysis_request = any(token in lower for token in ["analysis", "analy", "분석"])
        if is_report_request and is_analysis_request and "statistical_analysis" in available:
            steps = [
                ExecutionStep(1, "text_to_analytics", {"question": "user_input.request"}),
                ExecutionStep(2, "statistical_analysis", {"data": "step_1.output.data"}, [1]),
                ExecutionStep(3, "report_generation", {"data": "step_2.output.results"}, [2]),
            ]
            return ExecutionPlan(steps=steps, original_request=request)

        capability = "summarization" if any(token in lower for token in ["summar", "요약"]) and "summarization" in available else ""
        if not capability and available:
            capability = available[0]
        if not capability:
            return ExecutionPlan(steps=[], original_request=request)
        return ExecutionPlan(
            steps=[
                ExecutionStep(
                    step_number=1,
                    capability=capability,
                    input_mapping={"text": "user_input.request"},
                    depends_on=[],
                )
            ],
            original_request=request,
        )
