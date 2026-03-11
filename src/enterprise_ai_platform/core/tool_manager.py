from __future__ import annotations

from enterprise_ai_platform.tools.base_tool import BaseTool
from enterprise_ai_platform.models.domain import ToolDescriptor


class ToolManager:
    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        self._tools[tool.descriptor().tool_id] = tool

    async def invoke(self, tool_id: str, input_data: dict[str, object]) -> dict[str, object]:
        return await self._tools[tool_id].invoke(input_data)

    def list_tools(self) -> list[str]:
        return sorted(self._tools.keys())

    def has_tool(self, tool_id: str) -> bool:
        return tool_id in self._tools

    def descriptors(self) -> list[ToolDescriptor]:
        return [self._tools[tool_id].descriptor() for tool_id in self.list_tools()]
