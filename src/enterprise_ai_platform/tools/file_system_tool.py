from __future__ import annotations

from pathlib import Path

from enterprise_ai_platform.models.domain import ToolDescriptor
from enterprise_ai_platform.tools.base_tool import BaseTool


class FileSystemTool(BaseTool):
    def descriptor(self) -> ToolDescriptor:
        return ToolDescriptor(
            tool_id="filesystem",
            name="Filesystem Tool",
            description="Read file contents",
            input_schema={"type": "object", "properties": {"path": {"type": "string"}}},
            output_schema={"type": "object", "properties": {"content": {"type": "string"}}},
            transport="local",
        )

    async def invoke(self, input_data: dict[str, object]) -> dict[str, object]:
        file_path = Path(str(input_data.get("path", "")))
        return {"content": file_path.read_text(encoding="utf-8")}
