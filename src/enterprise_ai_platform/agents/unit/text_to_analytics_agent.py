from __future__ import annotations

from enterprise_ai_platform.agents.unit.common import JSONEchoAgent, trace, try_complete_json
from enterprise_ai_platform.core.agent_context import AgentContext
from enterprise_ai_platform.core.capability_registry import CapabilityRegistry
from enterprise_ai_platform.models.domain import AgentCategory, TaskInput


@CapabilityRegistry.register("text_to_analytics")
class TextToAnalyticsAgent(JSONEchoAgent):
    capability_name = "text_to_analytics"
    agent_id = "text_to_analytics_agent"
    name = "Text to Analytics Agent"
    description = "Generate SQL and analytics from questions"
    category = AgentCategory.ANALYTICS

    async def execute(self, task: TaskInput, context: AgentContext) -> dict[str, object]:
        question = str(task.payload.get("question", "")).strip()
        data_source = str(task.payload.get("data_source", "dataset")).strip() or "dataset"
        schema_hint = task.payload.get("schema_hint", {})
        llm_result = await try_complete_json(
            context,
            system_prompt=(
                "You translate analytics questions into safe read-only SQL. Return JSON only with keys "
                "sql, result_summary, data, and visualization_hint. Never emit mutating SQL."
            ),
            user_prompt=(
                f"Question: {question}\nData source: {data_source}\nSchema hint: {schema_hint}\n"
                "Generate a read-only SQL query and a short interpretation."
            ),
            schema={
                "type": "object",
                "properties": {
                    "sql": {"type": "string"},
                    "result_summary": {"type": "string"},
                    "data": {"type": "array"},
                    "visualization_hint": {"type": "string"},
                },
                "required": ["sql", "result_summary", "data", "visualization_hint"],
            },
            max_tokens=1200,
        )
        if llm_result is not None and "sql" in llm_result:
            trace(
                context,
                action="text_to_analytics_llm",
                input_summary=f"question={question[:50]}",
                output_summary="generated SQL",
            )
            return llm_result
        select_fields = "*"
        if isinstance(schema_hint, dict) and schema_hint:
            select_fields = ", ".join(str(key) for key in list(schema_hint.keys())[:5])
        sql = f"SELECT {select_fields} FROM {data_source} LIMIT 100;"
        data = [{"data_source": data_source, "question": question, "status": "simulated"}]
        trace(
            context,
            action="text_to_analytics",
            input_summary=f"question={question[:50]}",
            output_summary="generated SQL",
        )
        return {
            "sql": sql,
            "result_summary": f"Generated a safe read-only SQL template for '{question}'.",
            "data": data,
            "visualization_hint": "table",
        }
