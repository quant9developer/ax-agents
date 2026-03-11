from __future__ import annotations

from enterprise_ai_platform.models.domain import ToolDescriptor
from enterprise_ai_platform.tools.base_tool import BaseTool


class DatabaseTool(BaseTool):
    def descriptor(self) -> ToolDescriptor:
        return ToolDescriptor(
            tool_id="database",
            name="Database Tool",
            description="Read-only SQL execution stub",
            input_schema={"type": "object", "properties": {"query": {"type": "string"}}},
            output_schema={"type": "object", "properties": {"rows": {"type": "array"}}},
            transport="local",
        )

    async def invoke(self, input_data: dict[str, object]) -> dict[str, object]:
        query = str(input_data.get("query", ""))
        return {"rows": [], "query": query}
