from __future__ import annotations

import httpx

from enterprise_ai_platform.config import Settings
from enterprise_ai_platform.core.exceptions import ToolError
from enterprise_ai_platform.models.domain import ToolDescriptor
from enterprise_ai_platform.tools.base_tool import BaseTool


class MCPConnector(BaseTool):
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def descriptor(self) -> ToolDescriptor:
        return ToolDescriptor(
            tool_id="mcp",
            name="MCP Connector",
            description="Invoke configured MCP bridge servers over HTTP",
            input_schema={
                "type": "object",
                "properties": {
                    "server": {"type": "string"},
                    "tool": {"type": "string"},
                    "arguments": {"type": "object"},
                },
                "required": ["server", "tool"],
            },
            output_schema={
                "type": "object",
                "properties": {
                    "server": {"type": "string"},
                    "tool": {"type": "string"},
                    "result": {"type": "object"},
                    "transport": {"type": "string"},
                },
            },
            transport="mcp",
        )

    async def invoke(self, input_data: dict[str, object]) -> dict[str, object]:
        server_name = str(input_data.get("server", "")).strip()
        tool_name = str(input_data.get("tool", "")).strip()
        arguments = input_data.get("arguments", {})
        if not server_name or not tool_name:
            raise ToolError("MCP invocation requires 'server' and 'tool'")

        endpoint = self.settings.mcp_servers.get(server_name)
        if endpoint is None:
            available = ", ".join(sorted(self.settings.mcp_servers.keys())) or "none"
            raise ToolError(f"Unknown MCP server '{server_name}'. Available: {available}")

        if not endpoint:
            return {
                "server": server_name,
                "tool": tool_name,
                "result": {"status": "configured_without_endpoint", "arguments": arguments},
                "transport": "mcp",
            }

        payload = {"tool": tool_name, "arguments": arguments}
        try:
            async with httpx.AsyncClient(timeout=self.settings.llm_timeout_seconds) as client:
                response = await client.post(f"{endpoint.rstrip('/')}/invoke", json=payload)
            response.raise_for_status()
            result = response.json()
        except Exception as exc:
            raise ToolError(f"MCP bridge invocation failed: {exc}") from exc

        return {
            "server": server_name,
            "tool": tool_name,
            "result": result,
            "transport": "mcp",
        }
