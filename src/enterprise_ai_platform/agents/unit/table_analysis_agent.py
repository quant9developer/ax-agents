from __future__ import annotations

from enterprise_ai_platform.agents.unit.common import (
    JSONEchoAgent,
    basic_stats,
    normalize_rows,
    numeric_columns,
    trace,
)
from enterprise_ai_platform.core.agent_context import AgentContext
from enterprise_ai_platform.core.capability_registry import CapabilityRegistry
from enterprise_ai_platform.models.domain import AgentCategory, TaskInput


@CapabilityRegistry.register("table_analysis")
class TableAnalysisAgent(JSONEchoAgent):
    capability_name = "table_analysis"
    agent_id = "table_analysis_agent"
    name = "Table Analysis Agent"
    description = "Analyze table-shaped data"
    category = AgentCategory.ANALYTICS

    async def execute(self, task: TaskInput, context: AgentContext) -> dict[str, object]:
        rows = normalize_rows(task.payload.get("data", []))
        columns = numeric_columns(rows)
        statistics = {column: basic_stats(values) for column, values in columns.items()}
        patterns = [
            f"Column '{column}' has mean {stats['mean']} and std {stats['std']}."
            for column, stats in statistics.items()
        ]
        insights = [f"Processed {len(rows)} rows across {len(columns)} numeric columns."]
        trace(
            context,
            action="table_analysis",
            input_summary=f"{len(rows)} rows",
            output_summary=f"{len(statistics)} numeric columns",
        )
        return {
            "summary": f"Analyzed {len(rows)} rows of tabular data.",
            "statistics": statistics,
            "patterns": patterns,
            "insights": insights,
        }
