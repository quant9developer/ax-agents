from __future__ import annotations

from enterprise_ai_platform.agents.unit.common import (
    JSONEchoAgent,
    infer_output_language,
    trace,
    try_complete_json,
    unique_preserve_order,
)
from enterprise_ai_platform.core.agent_context import AgentContext
from enterprise_ai_platform.core.capability_registry import CapabilityRegistry
from enterprise_ai_platform.models.domain import AgentCategory, TaskInput


@CapabilityRegistry.register("report_generation")
class ReportGenerationAgent(JSONEchoAgent):
    capability_name = "report_generation"
    agent_id = "report_generation_agent"
    name = "Report Generation Agent"
    description = "Generate structured reports"
    category = AgentCategory.REPORTING
    timeout_seconds = 240

    async def execute(self, task: TaskInput, context: AgentContext) -> dict[str, object]:
        title = str(task.payload.get("title", "Generated Report"))
        data = task.payload.get("data", {})
        report_type = str(task.payload.get("report_type", "executive"))
        requested_sections = task.payload.get("sections", ["Overview", "Findings", "Next Steps"])
        output_language = infer_output_language(
            title,
            report_type,
            " ".join(str(item) for item in requested_sections) if isinstance(requested_sections, list) else "",
            requested=str(task.payload.get("output_language", "")),
        )
        llm_result = await try_complete_json(
            context,
            system_prompt=(
                "You generate concise business reports. Return JSON only with keys "
                "report_title, sections, executive_summary, and visualizations. "
                f"Write all natural-language fields in {output_language}."
            ),
            user_prompt=(
                f"Create a {report_type} report titled '{title}' using this data: {data}. "
                f"Requested sections: {requested_sections}. Output language: {output_language}."
            ),
            schema={
                "type": "object",
                "properties": {
                    "report_title": {"type": "string"},
                    "sections": {"type": "array"},
                    "executive_summary": {"type": "string"},
                    "visualizations": {"type": "array"},
                },
                "required": ["report_title", "sections", "executive_summary", "visualizations"],
            },
            max_tokens=1800,
        )
        if llm_result is not None and isinstance(llm_result.get("sections"), list):
            trace(
                context,
                action="report_generation_llm",
                input_summary=f"title={title[:50]}",
                output_summary=f"{len(llm_result['sections'])} report sections",
            )
            return llm_result
        section_names = [str(item) for item in requested_sections] if isinstance(requested_sections, list) else []
        if not section_names:
            section_names = ["Overview", "Findings", "Next Steps"]
        data_keys = unique_preserve_order(str(key) for key in data.keys()) if isinstance(data, dict) else []
        sections = [
            {
                "heading": section,
                "content": (
                    (
                        f"{section} 섹션입니다. "
                        f"가용 데이터 필드는 {', '.join(data_keys) if data_keys else '제공되지 않음'}입니다."
                    )
                    if output_language == "ko"
                    else (
                        f"{section} for a {report_type} report. "
                        f"Available data fields: {', '.join(data_keys) if data_keys else 'none provided'}."
                    )
                ),
                "data_refs": data_keys[:3],
            }
            for section in section_names
        ]
        visualizations = []
        if bool(task.payload.get("include_visualizations", True)) and data_keys:
            visualizations.append(
                {
                    "type": "table",
                    "title": f"{title} 데이터 개요" if output_language == "ko" else f"{title} data overview",
                    "data": data,
                }
            )
        trace(
            context,
            action="report_generation",
            input_summary=f"title={title[:50]}",
            output_summary=f"{len(sections)} report sections",
        )
        return {
            "report_title": title,
            "sections": sections,
            "executive_summary": (
                f"{title} 보고서는 {len(data_keys) or 1}개의 주요 데이터 영역을 요약합니다."
                if output_language == "ko"
                else f"{title} summarizes {len(data_keys) or 1} primary data areas."
            ),
            "visualizations": visualizations,
        }
