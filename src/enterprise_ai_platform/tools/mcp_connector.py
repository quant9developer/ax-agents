from __future__ import annotations

from enterprise_ai_platform.models.domain import ToolDescriptor
from enterprise_ai_platform.tools.base_tool import BaseTool


class MCPConnector(BaseTool):
    def descriptor(self) -> ToolDescriptor:
        return ToolDescriptor(
            tool_id="mcp",
            name="MCP Connector",
            description="MCP protocol adapter stub",
            input_schema={"type": "object"},
            output_schema={"type": "object"},
            transport="mcp",
        )

    async def invoke(self, input_data: dict[str, object]) -> dict[str, object]:
        return {"status": "ok", "echo": input_data}
