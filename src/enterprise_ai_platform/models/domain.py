from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class AgentCategory(StrEnum):
    RESEARCH = "research"
    DOCUMENT = "document"
    LANGUAGE = "language"
    ANALYTICS = "analytics"
    CODE = "code"
    REPORTING = "reporting"
    CLASSIFICATION = "classification"


class CapabilityDescriptor(BaseModel):
    name: str = Field(..., pattern=r"^[a-z_]+$", examples=["summarization"])
    description: str = Field(..., max_length=500)
    input_schema: dict[str, object]
    output_schema: dict[str, object]
    category: AgentCategory
    version: str = "1.0.0"


class AgentMetadata(BaseModel):
    agent_id: str = Field(..., pattern=r"^[a-z_]+$", examples=["summarization_agent"])
    name: str
    description: str
    category: AgentCategory
    capabilities: list[CapabilityDescriptor]
    version: str = "1.0.0"
    max_concurrent: int = Field(default=10, ge=1)
    timeout_seconds: int = Field(default=120, ge=1, le=3600)


class TaskStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskInput(BaseModel):
    capability: str
    payload: dict[str, object]
    config: dict[str, object] = Field(default_factory=dict)
    context: dict[str, object] = Field(default_factory=dict)


class ErrorDetail(BaseModel):
    code: str
    message: str
    retryable: bool = False


class TraceEntry(BaseModel):
    step: int
    action: str
    input_summary: str
    output_summary: str
    duration_ms: int
    metadata: dict[str, object] = Field(default_factory=dict)


class TaskResult(BaseModel):
    task_id: str
    status: TaskStatus
    agent_id: str
    output: dict[str, object] | None = None
    error: ErrorDetail | None = None
    traces: list[TraceEntry] = Field(default_factory=list)
    started_at: datetime
    completed_at: datetime | None = None
    duration_ms: int | None = None


class ToolDescriptor(BaseModel):
    tool_id: str
    name: str
    description: str
    input_schema: dict[str, object]
    output_schema: dict[str, object]
    transport: str = "mcp"
    endpoint: str | None = None
    auth_required: bool = False
