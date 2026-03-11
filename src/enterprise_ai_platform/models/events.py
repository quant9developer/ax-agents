from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel


class EventType(StrEnum):
    TASK_CREATED = "task.created"
    TASK_STARTED = "task.started"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"
    AGENT_INVOKED = "agent.invoked"
    TOOL_CALLED = "tool.called"


class PlatformEvent(BaseModel):
    event_id: str
    event_type: EventType
    timestamp: datetime
    payload: dict[str, object]
    source: str
    correlation_id: str
