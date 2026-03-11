from fastapi import APIRouter, Depends

from enterprise_ai_platform.dependencies import get_tool_manager
from enterprise_ai_platform.core.tool_manager import ToolManager

router = APIRouter(tags=["tools"])


@router.get("/tools")
def list_tools(tool_manager: ToolManager = Depends(get_tool_manager)) -> dict[str, object]:
    return {
        "tools": [
            {
                "tool_id": descriptor.tool_id,
                "name": descriptor.name,
                "description": descriptor.description,
                "transport": descriptor.transport,
                "endpoint": descriptor.endpoint,
            }
            for descriptor in tool_manager.descriptors()
        ]
    }
