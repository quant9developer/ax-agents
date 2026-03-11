from __future__ import annotations

from enterprise_ai_platform.agents.unit.common import (
    JSONEchoAgent,
    normalize_rows,
    numeric_columns,
    summarize_text,
    top_keywords,
    trace,
)
from enterprise_ai_platform.core.agent_context import AgentContext
from enterprise_ai_platform.core.capability_registry import CapabilityRegistry
from enterprise_ai_platform.models.domain import AgentCategory, TaskInput


@CapabilityRegistry.register("data_analysis")
class DataAnalysisAgent(JSONEchoAgent):
    capability_name = "data_analysis"
    agent_id = "data_analysis_agent"
    name = "Data Analysis Agent"
    description = "Find patterns and recommendations"
    category = AgentCategory.ANALYTICS

    async def execute(self, task: TaskInput, context: AgentContext) -> dict[str, object]:
        data = task.payload.get("data", "")
        goal = str(task.payload.get("goal", "Identify insights"))
        patterns: list[str] = []
        insights: list[str] = []
        recommendations: list[str] = []

        if isinstance(data, str):
            summary, key_points = summarize_text(data, max_words=80)
            patterns = [f"Frequent terms: {', '.join(keyword for keyword, _ in top_keywords(data, 5))}"]
            insights = key_points or [summary]
        else:
            rows = normalize_rows(data)
            columns = numeric_columns(rows)
            patterns = [f"{column} contains {len(values)} numeric observations." for column, values in columns.items()]
            insights = [f"Dataset includes {len(rows)} rows and {len(columns)} measurable columns."]

        recommendations.append(f"Focus follow-up analysis on: {goal}.")
        confidence = 0.7 if insights else 0.4
        trace(
            context,
            action="data_analysis",
            input_summary=f"goal={goal[:50]}",
            output_summary=f"{len(insights)} insights",
        )
        return {
            "patterns": patterns or ["No clear patterns detected from local analysis."],
            "insights": insights or ["No strong insights available from provided input."],
            "recommendations": recommendations,
            "confidence": confidence,
        }
