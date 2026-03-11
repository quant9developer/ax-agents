from __future__ import annotations

import httpx

from enterprise_ai_platform.models.domain import ToolDescriptor
from enterprise_ai_platform.tools.base_tool import BaseTool


class HttpTool(BaseTool):
    def descriptor(self) -> ToolDescriptor:
        return ToolDescriptor(
            tool_id="http",
            name="HTTP Tool",
            description="Execute HTTP GET requests",
            input_schema={"type": "object", "properties": {"url": {"type": "string"}}},
            output_schema={"type": "object", "properties": {"status_code": {"type": "integer"}}},
            transport="http",
        )

    async def invoke(self, input_data: dict[str, object]) -> dict[str, object]:
        url = str(input_data.get("url", ""))
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
            return {"status_code": resp.status_code, "text": resp.text[:2000]}
