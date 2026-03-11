# specs.md

# Project: Enterprise AI Agent Platform

---

# 1. Overview

Build a **production-ready Enterprise AI Agent Platform** that enables organizations to deploy **AI-powered agents across multiple business functions**.

The platform provides a **general-purpose agent infrastructure** that supports:

* task automation
* knowledge retrieval
* analytics
* document processing
* software development assistance
* customer service operations

Rather than building isolated AI applications, the platform enables organizations to **compose specialized AI agents and tools into intelligent workflows**.

---

## Platform Vision

The system functions as an **Enterprise AI Agent Operating System**, enabling:

* reusable AI capabilities
* modular agents
* enterprise tool integration
* scalable orchestration of AI tasks

Agents can collaborate, invoke tools, retrieve knowledge, and generate outputs for a wide range of enterprise use cases.

---

# 2. Technology Stack

## Required Technologies

| Layer            | Technology                          | Version   |
| ---------------- | ----------------------------------- | --------- |
| Language         | Python                              | 3.11+     |
| Web Framework    | FastAPI                             | 0.110+    |
| Async Runtime    | uvicorn                             | 0.29+     |
| LLM Client       | litellm or openai SDK               | latest    |
| Vector Store     | ChromaDB (default), Pinecone (opt)  | latest    |
| Database         | PostgreSQL                          | 16+       |
| ORM              | SQLAlchemy 2.0 (async)              | 2.0+      |
| Cache            | Redis                               | 7+        |
| Task Queue       | Celery + Redis broker               | 5.3+      |
| Containerization | Docker, Docker Compose              | latest    |
| Testing          | pytest, pytest-asyncio              | latest    |
| Linting          | ruff                                | latest    |
| Type Checking    | mypy (strict mode)                  | latest    |

## Python Package Structure

```
pyproject.toml          # Single source of truth for dependencies
```

All packages must be typed. No `Any` types in public interfaces.

---

# 3. Project Directory Structure

```
enterprise-ai-platform/
│
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
├── alembic.ini
├── .env.example
├── README.md
│
├── alembic/
│   └── versions/
│
├── src/
│   └── platform/
│       ├── __init__.py
│       ├── main.py                          # FastAPI app factory
│       ├── config.py                        # Settings (pydantic-settings)
│       ├── dependencies.py                  # FastAPI dependency injection
│       │
│       ├── api/
│       │   ├── __init__.py
│       │   ├── router.py                    # Root router aggregator
│       │   ├── v1/
│       │   │   ├── __init__.py
│       │   │   ├── agents.py                # POST /v1/agents/execute
│       │   │   ├── tasks.py                 # POST /v1/tasks
│       │   │   ├── capabilities.py          # GET  /v1/capabilities
│       │   │   ├── tools.py                 # Tool management endpoints
│       │   │   ├── knowledge.py             # Knowledge base endpoints
│       │   │   └── health.py                # GET  /v1/health
│       │   └── middleware/
│       │       ├── __init__.py
│       │       ├── auth.py
│       │       ├── rate_limit.py
│       │       └── request_logging.py
│       │
│       ├── core/
│       │   ├── __init__.py
│       │   ├── base_agent.py                # Abstract base for all agents
│       │   ├── agent_context.py             # Runtime context passed to agents
│       │   ├── capability_registry.py       # Global capability → agent mapping
│       │   ├── capability_graph.py          # Graph-based orchestration engine
│       │   ├── orchestrator.py              # Multi-step task orchestrator
│       │   ├── tool_manager.py              # Tool loading and invocation
│       │   ├── llm_client.py                # Unified LLM interface
│       │   ├── event_bus.py                 # Async event publish/subscribe
│       │   └── exceptions.py                # Platform-wide exception hierarchy
│       │
│       ├── agents/
│       │   ├── __init__.py
│       │   ├── unit/
│       │   │   ├── __init__.py
│       │   │   ├── deep_research_agent.py
│       │   │   ├── web_search_agent.py
│       │   │   ├── ocr_agent.py
│       │   │   ├── text_to_analytics_agent.py
│       │   │   ├── code_generation_agent.py
│       │   │   ├── code_refactor_agent.py
│       │   │   ├── report_generation_agent.py
│       │   │   ├── translation_agent.py
│       │   │   ├── document_drafting_agent.py
│       │   │   ├── summarization_agent.py
│       │   │   ├── proofreading_agent.py
│       │   │   ├── keyword_extraction_agent.py
│       │   │   ├── table_analysis_agent.py
│       │   │   ├── document_comparison_agent.py
│       │   │   ├── statistical_analysis_agent.py
│       │   │   ├── data_analysis_agent.py
│       │   │   └── classification_agent.py
│       │   │
│       │   └── application/
│       │       ├── __init__.py
│       │       ├── call_assistant_agent.py
│       │       ├── call_evaluation_agent.py
│       │       ├── chatbot_agent.py
│       │       └── research_workflow_agent.py
│       │
│       ├── tools/
│       │   ├── __init__.py
│       │   ├── base_tool.py                 # Abstract tool interface
│       │   ├── mcp_connector.py             # MCP protocol client
│       │   ├── database_tool.py
│       │   ├── file_system_tool.py
│       │   └── http_tool.py
│       │
│       ├── knowledge/
│       │   ├── __init__.py
│       │   ├── vector_store.py              # ChromaDB / Pinecone abstraction
│       │   ├── document_loader.py           # PDF, DOCX, TXT → chunks
│       │   ├── embeddings.py                # Embedding model interface
│       │   └── retriever.py                 # Search + rerank pipeline
│       │
│       ├── models/
│       │   ├── __init__.py
│       │   ├── domain.py                    # Pydantic domain models
│       │   ├── db.py                        # SQLAlchemy ORM models
│       │   └── events.py                    # Event payload models
│       │
│       ├── services/
│       │   ├── __init__.py
│       │   ├── task_service.py              # Business logic for task lifecycle
│       │   ├── agent_service.py             # Agent instantiation + execution
│       │   └── knowledge_service.py         # Knowledge base CRUD
│       │
│       ├── observability/
│       │   ├── __init__.py
│       │   ├── tracer.py                    # OpenTelemetry tracing
│       │   ├── logger.py                    # Structured JSON logging
│       │   └── metrics.py                   # Prometheus metrics
│       │
│       └── security/
│           ├── __init__.py
│           ├── auth.py                      # JWT / API key validation
│           ├── rbac.py                      # Role-based access control
│           └── audit.py                     # Audit log writer
│
└── tests/
    ├── conftest.py                          # Shared fixtures
    ├── unit/
    │   ├── test_base_agent.py
    │   ├── test_capability_registry.py
    │   ├── test_capability_graph.py
    │   ├── test_orchestrator.py
    │   └── agents/
    │       └── test_summarization_agent.py
    ├── integration/
    │   ├── test_api_agents.py
    │   └── test_task_lifecycle.py
    └── e2e/
        └── test_workflows.py
```

---

# 4. Core Data Models

All models use **Pydantic v2** for validation and serialization.

## 4.1 Agent Identity and Capability

```python
# src/platform/models/domain.py

from enum import StrEnum
from pydantic import BaseModel, Field
from datetime import datetime


class AgentCategory(StrEnum):
    RESEARCH = "research"
    DOCUMENT = "document"
    LANGUAGE = "language"
    ANALYTICS = "analytics"
    CODE = "code"
    REPORTING = "reporting"
    CLASSIFICATION = "classification"


class CapabilityDescriptor(BaseModel):
    """Describes a single capability an agent can perform."""
    name: str = Field(..., pattern=r"^[a-z_]+$", examples=["summarization"])
    description: str = Field(..., max_length=500)
    input_schema: dict     # JSON Schema for expected input
    output_schema: dict    # JSON Schema for expected output
    category: AgentCategory
    version: str = "1.0.0"


class AgentMetadata(BaseModel):
    """Static metadata that every agent must declare."""
    agent_id: str = Field(..., pattern=r"^[a-z_]+$", examples=["summarization_agent"])
    name: str
    description: str
    category: AgentCategory
    capabilities: list[CapabilityDescriptor]
    version: str = "1.0.0"
    max_concurrent: int = Field(default=10, ge=1)
    timeout_seconds: int = Field(default=120, ge=1, le=3600)
```

## 4.2 Task Model (request → execution → result)

```python
class TaskStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskInput(BaseModel):
    """Input payload sent by callers."""
    capability: str                       # e.g. "summarization"
    payload: dict                         # Capability-specific data
    config: dict = Field(default_factory=dict)  # Optional overrides
    context: dict = Field(default_factory=dict)  # Extra context (user info, etc.)


class TaskResult(BaseModel):
    """Standardized result returned by every agent."""
    task_id: str
    status: TaskStatus
    agent_id: str
    output: dict | None = None
    error: "ErrorDetail | None" = None
    traces: list["TraceEntry"] = Field(default_factory=list)
    started_at: datetime
    completed_at: datetime | None = None
    duration_ms: int | None = None


class ErrorDetail(BaseModel):
    code: str                             # Machine-readable e.g. "LLM_TIMEOUT"
    message: str                          # Human-readable description
    retryable: bool = False


class TraceEntry(BaseModel):
    """Single step inside an agent execution for observability."""
    step: int
    action: str                           # e.g. "llm_call", "tool_invoke", "retrieval"
    input_summary: str
    output_summary: str
    duration_ms: int
    metadata: dict = Field(default_factory=dict)
```

## 4.3 Tool Model

```python
class ToolDescriptor(BaseModel):
    """Describes an external tool agents can invoke."""
    tool_id: str
    name: str
    description: str
    input_schema: dict        # JSON Schema
    output_schema: dict       # JSON Schema
    transport: str = "mcp"    # "mcp" | "http" | "local"
    endpoint: str | None = None
    auth_required: bool = False
```

## 4.4 Event Model

```python
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
    payload: dict
    source: str              # Agent or service that emitted this
    correlation_id: str      # Links events in the same task chain
```

---

# 5. Core Interfaces (Abstract Base Classes)

## 5.1 BaseAgent — All agents must extend this

```python
# src/platform/core/base_agent.py

from abc import ABC, abstractmethod
from platform.models.domain import (
    AgentMetadata, TaskInput, TaskResult, TraceEntry, TaskStatus, ErrorDetail
)
from platform.core.agent_context import AgentContext
import uuid
from datetime import datetime, timezone


class BaseAgent(ABC):
    """Abstract base class for all agents (unit and application)."""

    @abstractmethod
    def metadata(self) -> AgentMetadata:
        """Return static metadata describing this agent and its capabilities."""
        ...

    @abstractmethod
    async def execute(self, task: TaskInput, context: AgentContext) -> dict:
        """
        Execute the agent's core logic.

        Args:
            task: The validated input for this capability.
            context: Runtime context with access to LLM, tools, knowledge, config.

        Returns:
            dict matching the capability's output_schema.

        Raises:
            AgentError: On recoverable errors (will be caught and wrapped).
        """
        ...

    async def run(self, task: TaskInput, context: AgentContext) -> TaskResult:
        """
        Orchestration wrapper. Do NOT override this.
        Handles lifecycle, tracing, error wrapping.
        """
        task_id = uuid.uuid4().hex
        started = datetime.now(timezone.utc)
        try:
            output = await self.execute(task, context)
            return TaskResult(
                task_id=task_id,
                status=TaskStatus.COMPLETED,
                agent_id=self.metadata().agent_id,
                output=output,
                started_at=started,
                completed_at=datetime.now(timezone.utc),
                duration_ms=_elapsed_ms(started),
                traces=context.traces,
            )
        except Exception as exc:
            return TaskResult(
                task_id=task_id,
                status=TaskStatus.FAILED,
                agent_id=self.metadata().agent_id,
                error=ErrorDetail(
                    code=type(exc).__name__,
                    message=str(exc),
                    retryable=getattr(exc, "retryable", False),
                ),
                started_at=started,
                completed_at=datetime.now(timezone.utc),
                duration_ms=_elapsed_ms(started),
                traces=context.traces,
            )
```

## 5.2 AgentContext — Runtime dependencies injected into agents

```python
# src/platform/core/agent_context.py

from dataclasses import dataclass, field
from platform.core.llm_client import LLMClient
from platform.core.tool_manager import ToolManager
from platform.knowledge.retriever import Retriever
from platform.models.domain import TraceEntry


@dataclass
class AgentContext:
    """Injected into every agent at execution time."""
    llm: LLMClient
    tools: ToolManager
    knowledge: Retriever
    config: dict = field(default_factory=dict)
    traces: list[TraceEntry] = field(default_factory=list)
    correlation_id: str = ""
    user_id: str | None = None
    tenant_id: str | None = None

    def add_trace(self, step: int, action: str,
                  input_summary: str, output_summary: str,
                  duration_ms: int, **metadata) -> None:
        self.traces.append(TraceEntry(
            step=step, action=action,
            input_summary=input_summary,
            output_summary=output_summary,
            duration_ms=duration_ms,
            metadata=metadata,
        ))
```

## 5.3 LLMClient — Unified LLM interface

```python
# src/platform/core/llm_client.py

from dataclasses import dataclass


@dataclass
class LLMRequest:
    messages: list[dict]               # OpenAI-format messages
    model: str = "gpt-4o"             # Default model, configurable
    temperature: float = 0.2
    max_tokens: int = 4096
    response_format: dict | None = None  # JSON mode schema if needed
    tools: list[dict] | None = None      # Function calling tools


@dataclass
class LLMResponse:
    content: str
    model: str
    usage: dict                        # {"prompt_tokens": ..., "completion_tokens": ...}
    tool_calls: list[dict] | None = None
    raw: dict | None = None            # Full API response for debugging


class LLMClient:
    """
    Unified LLM interface. Implementations should wrap litellm or openai SDK.
    Must support: completion, structured output (JSON mode), function calling.
    """

    async def complete(self, request: LLMRequest) -> LLMResponse:
        """Send a completion request. Handles retries internally."""
        ...

    async def complete_json(self, request: LLMRequest,
                            schema: dict) -> dict:
        """
        Completion with guaranteed JSON output matching the given schema.
        Uses response_format or prompt engineering as fallback.
        """
        ...
```

## 5.4 BaseTool — Tool interface

```python
# src/platform/tools/base_tool.py

from abc import ABC, abstractmethod
from platform.models.domain import ToolDescriptor


class BaseTool(ABC):

    @abstractmethod
    def descriptor(self) -> ToolDescriptor:
        """Return tool metadata and schemas."""
        ...

    @abstractmethod
    async def invoke(self, input_data: dict) -> dict:
        """
        Execute the tool with validated input.

        Returns:
            dict matching the tool's output_schema.

        Raises:
            ToolError on failure.
        """
        ...
```

---

# 6. Capability Registry and Graph

## 6.1 Capability Registry

```python
# src/platform/core/capability_registry.py

class CapabilityRegistry:
    """
    Global registry mapping capability names to agent classes.
    Agents self-register at import time via decorator.
    """

    _registry: dict[str, type[BaseAgent]] = {}

    @classmethod
    def register(cls, capability_name: str):
        """Decorator to register an agent for a capability."""
        def wrapper(agent_cls: type[BaseAgent]):
            cls._registry[capability_name] = agent_cls
            return agent_cls
        return wrapper

    @classmethod
    def resolve(cls, capability: str) -> type[BaseAgent]:
        """Resolve a capability name to an agent class. Raises KeyError if not found."""
        if capability not in cls._registry:
            raise KeyError(
                f"No agent registered for capability '{capability}'. "
                f"Available: {list(cls._registry.keys())}"
            )
        return cls._registry[capability]

    @classmethod
    def list_capabilities(cls) -> list[str]:
        return list(cls._registry.keys())
```

### Registration pattern (every agent must do this)

```python
# Example: src/platform/agents/unit/summarization_agent.py

from platform.core.capability_registry import CapabilityRegistry
from platform.core.base_agent import BaseAgent

@CapabilityRegistry.register("summarization")
class SummarizationAgent(BaseAgent):
    ...
```

## 6.2 Capability Graph — Multi-step orchestration

```python
# src/platform/core/capability_graph.py

from dataclasses import dataclass


@dataclass
class ExecutionStep:
    """One step in an execution plan."""
    step_number: int
    capability: str
    input_mapping: dict   # Maps keys from previous step outputs to this step's input
    depends_on: list[int] = field(default_factory=list)  # step_numbers this depends on


@dataclass
class ExecutionPlan:
    """Ordered list of steps resolved by the capability graph."""
    steps: list[ExecutionStep]
    original_request: str


class CapabilityGraph:
    """
    Resolves a natural language request into an ExecutionPlan.

    Resolution strategies (implement in order of priority):
    1. Rule-based: Pattern matching for known multi-step workflows.
    2. LLM-based: Use LLM to decompose complex requests into capabilities.

    The graph also supports parallel execution when steps have no dependencies.
    """

    def __init__(self, registry: CapabilityRegistry, llm: LLMClient):
        self.registry = registry
        self.llm = llm

    async def resolve(self, request: str) -> ExecutionPlan:
        """
        Decompose a user request into an ordered execution plan.

        Steps:
        1. Send request + available capabilities list to LLM.
        2. LLM returns structured JSON with ordered steps.
        3. Validate each step's capability exists in registry.
        4. Return ExecutionPlan.
        """
        ...
```

### LLM Prompt Template for Graph Resolution

```
You are a task planner for an AI agent platform.

Available capabilities:
{capabilities_list}

User request:
"{user_request}"

Respond in JSON only (no markdown):
{
  "steps": [
    {
      "step_number": 1,
      "capability": "<capability_name>",
      "input_mapping": {"<target_key>": "<source: 'user_input' or 'step_N.output_key'>"},
      "depends_on": []
    }
  ]
}

Rules:
- Use ONLY capabilities from the available list.
- Minimize the number of steps.
- Steps with no dependencies can run in parallel.
- input_mapping uses "user_input.<key>" for original request data,
  or "step_<N>.output.<key>" for outputs from previous steps.
```

---

# 7. Orchestrator

```python
# src/platform/core/orchestrator.py

class Orchestrator:
    """
    Executes an ExecutionPlan by running agents in dependency order.
    Supports both sequential and parallel execution.
    """

    def __init__(self, registry: CapabilityRegistry, context_factory):
        self.registry = registry
        self.context_factory = context_factory

    async def execute_plan(self, plan: ExecutionPlan,
                           initial_input: dict) -> TaskResult:
        """
        Execute an entire plan.

        Algorithm:
        1. Build dependency graph from plan.steps.
        2. Run steps with no dependencies first (parallel via asyncio.gather).
        3. Feed outputs into dependent steps via input_mapping.
        4. Collect all step results.
        5. Return final TaskResult with merged outputs.

        Error handling:
        - If a step fails and is marked retryable, retry up to 2 times.
        - If a step fails permanently, mark the entire plan as FAILED.
        - Always collect traces from all completed steps.
        """
        ...
```

---

# 8. API Endpoints

## 8.1 Execute a Single Agent

```
POST /v1/agents/execute
```

Request body:

```json
{
  "capability": "summarization",
  "payload": {
    "text": "Long document text here...",
    "max_length": 200
  },
  "config": {
    "model": "gpt-4o",
    "temperature": 0.3
  }
}
```

Response (200):

```json
{
  "task_id": "abc123",
  "status": "completed",
  "agent_id": "summarization_agent",
  "output": {
    "summary": "...",
    "key_points": ["...", "..."]
  },
  "traces": [
    {
      "step": 1,
      "action": "llm_call",
      "input_summary": "Summarize text (2340 tokens)",
      "output_summary": "Generated summary (85 tokens)",
      "duration_ms": 1230
    }
  ],
  "started_at": "2025-01-01T00:00:00Z",
  "completed_at": "2025-01-01T00:00:01Z",
  "duration_ms": 1230
}
```

Response (400 — validation error):

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "payload.text is required",
    "retryable": false
  }
}
```

Response (404 — unknown capability):

```json
{
  "error": {
    "code": "CAPABILITY_NOT_FOUND",
    "message": "No agent registered for capability 'unknown'",
    "retryable": false
  }
}
```

## 8.2 Submit a Multi-Step Task

```
POST /v1/tasks
```

Request body:

```json
{
  "request": "Analyze last quarter's sales data and generate an executive report",
  "payload": {
    "data_source": "sales_db",
    "quarter": "Q3-2024"
  }
}
```

Response (202 — accepted for async execution):

```json
{
  "task_id": "task_789",
  "status": "pending",
  "plan": {
    "steps": [
      {"step_number": 1, "capability": "text_to_analytics", "depends_on": []},
      {"step_number": 2, "capability": "statistical_analysis", "depends_on": [1]},
      {"step_number": 3, "capability": "report_generation", "depends_on": [2]}
    ]
  }
}
```

## 8.3 List Capabilities

```
GET /v1/capabilities
```

Response (200):

```json
{
  "capabilities": [
    {
      "name": "summarization",
      "description": "Summarize long documents or text",
      "category": "document",
      "agent_id": "summarization_agent",
      "input_schema": { ... },
      "output_schema": { ... }
    }
  ]
}
```

## 8.4 Health Check

```
GET /v1/health
```

Response (200):

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "agents_loaded": 17,
  "uptime_seconds": 3600
}
```

---

# 9. Unit Agent Specifications

Each unit agent below includes: purpose, registered capability name, input schema, output schema, and implementation notes.

---

## 9.1 Research and Information Agents

### Deep Research Agent

| Field           | Value                        |
| --------------- | ---------------------------- |
| agent_id        | `deep_research_agent`        |
| capability      | `deep_research`              |
| category        | `research`                   |
| timeout_seconds | 300                          |

**Input schema:**

```json
{
  "topic": "string (required)",
  "depth": "string enum: 'brief' | 'standard' | 'comprehensive'. Default: 'standard'",
  "sources_limit": "integer. Default: 10",
  "output_format": "string enum: 'structured' | 'narrative'. Default: 'structured'"
}
```

**Output schema:**

```json
{
  "summary": "string",
  "key_insights": ["string"],
  "supporting_evidence": [
    {"claim": "string", "source": "string", "confidence": "float 0-1"}
  ],
  "confidence": "float 0-1"
}
```

**Implementation notes:**

1. Call `context.tools.invoke("web_search", ...)` for multiple search queries.
2. Use `context.knowledge.search(topic)` for internal knowledge base.
3. Send all gathered evidence to LLM with structured output prompt.
4. Use `context.llm.complete_json(...)` to produce the output.
5. Add trace entry for each search and LLM call.

---

### Web Search Agent

| Field           | Value                 |
| --------------- | --------------------- |
| agent_id        | `web_search_agent`    |
| capability      | `web_search`          |
| category        | `research`            |
| timeout_seconds | 60                    |

**Input schema:**

```json
{
  "query": "string (required)",
  "max_results": "integer. Default: 5. Max: 20",
  "include_snippets": "boolean. Default: true"
}
```

**Output schema:**

```json
{
  "results": [
    {
      "title": "string",
      "url": "string",
      "snippet": "string",
      "relevance_score": "float 0-1"
    }
  ],
  "query_used": "string"
}
```

**Implementation notes:**

1. Invoke a web search tool via `context.tools.invoke("web_search", {"query": ...})`.
2. Optionally re-rank results using LLM if relevance scoring is needed.
3. Return structured results.

---

## 9.2 Document Intelligence Agents

### OCR Agent

| Field           | Value          |
| --------------- | -------------- |
| agent_id        | `ocr_agent`   |
| capability      | `ocr`          |
| category        | `document`     |
| timeout_seconds | 120            |

**Input schema:**

```json
{
  "file_path": "string (required) — path to image or scanned PDF",
  "file_type": "string enum: 'image' | 'pdf'. Required.",
  "extract_tables": "boolean. Default: false",
  "language": "string. Default: 'eng'"
}
```

**Output schema:**

```json
{
  "text": "string",
  "tables": [
    {
      "headers": ["string"],
      "rows": [["string"]]
    }
  ],
  "pages": "integer",
  "confidence": "float 0-1"
}
```

**Implementation notes:**

1. Use Tesseract (default) or PaddleOCR via tool invocation.
2. For PDFs, convert each page to image first (pdf2image).
3. If `extract_tables` is true, use table detection before OCR.
4. Return aggregated text across all pages.

---

### Document Drafting Agent

| Field           | Value                       |
| --------------- | --------------------------- |
| agent_id        | `document_drafting_agent`   |
| capability      | `document_drafting`         |
| category        | `document`                  |
| timeout_seconds | 180                         |

**Input schema:**

```json
{
  "document_type": "string enum: 'report' | 'proposal' | 'memo' | 'manual' | 'letter'. Required.",
  "topic": "string (required)",
  "outline": "list[string] (optional) — section headings",
  "tone": "string enum: 'formal' | 'casual' | 'technical'. Default: 'formal'",
  "max_words": "integer. Default: 2000"
}
```

**Output schema:**

```json
{
  "title": "string",
  "sections": [
    {"heading": "string", "content": "string"}
  ],
  "word_count": "integer"
}
```

---

### Document Summarization Agent

| Field           | Value                    |
| --------------- | ------------------------ |
| agent_id        | `summarization_agent`    |
| capability      | `summarization`          |
| category        | `document`               |
| timeout_seconds | 120                      |

**Input schema:**

```json
{
  "text": "string (required)",
  "max_length": "integer (optional). Target summary length in words.",
  "style": "string enum: 'executive' | 'bullet_points' | 'narrative'. Default: 'executive'"
}
```

**Output schema:**

```json
{
  "summary": "string",
  "key_points": ["string"],
  "original_length": "integer (word count)",
  "summary_length": "integer (word count)"
}
```

---

### Document Comparison Agent

| Field           | Value                          |
| --------------- | ------------------------------ |
| agent_id        | `document_comparison_agent`    |
| capability      | `document_comparison`          |
| category        | `document`                     |
| timeout_seconds | 180                            |

**Input schema:**

```json
{
  "document_a": "string (required) — text content of first document",
  "document_b": "string (required) — text content of second document",
  "comparison_type": "string enum: 'full' | 'structural' | 'semantic'. Default: 'full'"
}
```

**Output schema:**

```json
{
  "differences": [
    {
      "location": "string (section/paragraph reference)",
      "type": "string enum: 'added' | 'removed' | 'modified'",
      "document_a_text": "string",
      "document_b_text": "string",
      "significance": "string enum: 'high' | 'medium' | 'low'"
    }
  ],
  "summary": "string",
  "similarity_score": "float 0-1"
}
```

---

### Proofreading Agent

| Field           | Value                  |
| --------------- | ---------------------- |
| agent_id        | `proofreading_agent`   |
| capability      | `proofreading`         |
| category        | `document`             |
| timeout_seconds | 120                    |

**Input schema:**

```json
{
  "text": "string (required)",
  "focus": "string enum: 'grammar' | 'style' | 'tone' | 'all'. Default: 'all'",
  "target_tone": "string (optional). e.g., 'professional', 'friendly'"
}
```

**Output schema:**

```json
{
  "corrected_text": "string",
  "suggestions": [
    {
      "original": "string",
      "replacement": "string",
      "reason": "string",
      "category": "string enum: 'grammar' | 'style' | 'tone' | 'spelling'"
    }
  ],
  "total_changes": "integer"
}
```

---

## 9.3 Language Processing Agents

### Translation Agent

| Field           | Value                |
| --------------- | -------------------- |
| agent_id        | `translation_agent`  |
| capability      | `translation`        |
| category        | `language`           |
| timeout_seconds | 120                  |

**Input schema:**

```json
{
  "text": "string (required)",
  "source_language": "string (optional — auto-detect if omitted). ISO 639-1 code.",
  "target_language": "string (required). ISO 639-1 code.",
  "preserve_formatting": "boolean. Default: true"
}
```

**Output schema:**

```json
{
  "translated_text": "string",
  "source_language": "string (detected or confirmed)",
  "target_language": "string",
  "word_count": "integer"
}
```

---

### Keyword Extraction Agent

| Field           | Value                       |
| --------------- | --------------------------- |
| agent_id        | `keyword_extraction_agent`  |
| capability      | `keyword_extraction`        |
| category        | `language`                  |
| timeout_seconds | 60                          |

**Input schema:**

```json
{
  "text": "string (required)",
  "max_keywords": "integer. Default: 10",
  "include_entities": "boolean. Default: true"
}
```

**Output schema:**

```json
{
  "keywords": [
    {"keyword": "string", "relevance": "float 0-1"}
  ],
  "entities": [
    {"text": "string", "type": "string enum: 'person' | 'org' | 'location' | 'date' | 'other'"}
  ]
}
```

---

## 9.4 Data and Analytics Agents

### Text-to-Analytics Agent

| Field           | Value                        |
| --------------- | ---------------------------- |
| agent_id        | `text_to_analytics_agent`    |
| capability      | `text_to_analytics`          |
| category        | `analytics`                  |
| timeout_seconds | 120                          |

**Input schema:**

```json
{
  "question": "string (required). Natural language analytics question.",
  "data_source": "string (required). Database or dataset identifier.",
  "schema_hint": "dict (optional). Table and column descriptions to aid SQL generation."
}
```

**Output schema:**

```json
{
  "sql": "string",
  "result_summary": "string",
  "data": [{"column": "value"}],
  "visualization_hint": "string enum: 'bar_chart' | 'line_chart' | 'table' | 'pie_chart' | 'none'"
}
```

**Implementation notes:**

1. Use `schema_hint` or query the data source metadata for table schemas.
2. Generate SQL via LLM (`context.llm.complete_json(...)`).
3. Execute SQL via `context.tools.invoke("database", {"query": sql})`.
4. Summarize results via LLM.
5. **Never execute raw SQL without parameterization.** Use read-only connections.

---

### Table Data Analysis Agent

| Field           | Value                     |
| --------------- | ------------------------- |
| agent_id        | `table_analysis_agent`    |
| capability      | `table_analysis`          |
| category        | `analytics`               |
| timeout_seconds | 180                       |

**Input schema:**

```json
{
  "file_path": "string (optional). Path to CSV/Excel file.",
  "data": "list[dict] (optional). Inline tabular data.",
  "analysis_type": "string enum: 'descriptive' | 'correlation' | 'pattern' | 'full'. Default: 'full'",
  "question": "string (optional). Specific question about the data."
}
```

**Output schema:**

```json
{
  "summary": "string",
  "statistics": {"column_name": {"mean": 0, "median": 0, "std": 0}},
  "patterns": ["string"],
  "insights": ["string"]
}
```

---

### Statistical Analysis and Forecasting Agent

| Field           | Value                           |
| --------------- | ------------------------------- |
| agent_id        | `statistical_analysis_agent`    |
| capability      | `statistical_analysis`          |
| category        | `analytics`                     |
| timeout_seconds | 300                             |

**Input schema:**

```json
{
  "data": "list[dict] (required). Time series or tabular data.",
  "analysis_type": "string enum: 'regression' | 'forecast' | 'anomaly_detection' | 'descriptive'. Required.",
  "target_column": "string (required for regression/forecast).",
  "forecast_periods": "integer (optional). Number of periods to forecast. Default: 10.",
  "confidence_level": "float. Default: 0.95"
}
```

**Output schema:**

```json
{
  "model": "string (model name used, e.g. 'ARIMA', 'linear_regression')",
  "results": "dict (model-specific results)",
  "forecast": [{"period": "string", "value": "float", "lower": "float", "upper": "float"}],
  "metrics": {"rmse": "float", "r_squared": "float"},
  "visualization_data": "dict (plot-ready data)"
}
```

---

### Data Analysis Agent

| Field           | Value                  |
| --------------- | ---------------------- |
| agent_id        | `data_analysis_agent`  |
| capability      | `data_analysis`        |
| category        | `analytics`            |
| timeout_seconds | 180                    |

**Input schema:**

```json
{
  "data": "string | list[dict] (required). Unstructured text or structured data.",
  "goal": "string (required). What the user wants to learn.",
  "output_format": "string enum: 'insights' | 'report' | 'recommendations'. Default: 'insights'"
}
```

**Output schema:**

```json
{
  "patterns": ["string"],
  "insights": ["string"],
  "recommendations": ["string"],
  "confidence": "float 0-1"
}
```

---

## 9.5 Code Intelligence Agents

### Code Generation Agent

| Field           | Value                      |
| --------------- | -------------------------- |
| agent_id        | `code_generation_agent`    |
| capability      | `code_generation`          |
| category        | `code`                     |
| timeout_seconds | 120                        |

**Input schema:**

```json
{
  "requirement": "string (required). Natural language description.",
  "language": "string. Default: 'python'",
  "framework": "string (optional). e.g. 'fastapi', 'react'",
  "style_guide": "string (optional). Coding conventions to follow."
}
```

**Output schema:**

```json
{
  "language": "string",
  "code": "string",
  "explanation": "string",
  "dependencies": ["string"],
  "test_code": "string (optional unit test)"
}
```

---

### Code Understanding and Refactoring Agent

| Field           | Value                  |
| --------------- | ---------------------- |
| agent_id        | `code_refactor_agent`  |
| capability      | `code_refactor`        |
| category        | `code`                 |
| timeout_seconds | 120                    |

**Input schema:**

```json
{
  "code": "string (required). Source code to analyze.",
  "language": "string. Default: 'python'",
  "action": "string enum: 'explain' | 'refactor' | 'optimize' | 'review'. Default: 'refactor'"
}
```

**Output schema:**

```json
{
  "refactored_code": "string (if action is refactor/optimize)",
  "explanation": "string",
  "improvements": [
    {"description": "string", "severity": "string enum: 'high' | 'medium' | 'low'"}
  ],
  "quality_score": "float 0-1"
}
```

---

## 9.6 Reporting Agents

### Report Generation Agent

| Field           | Value                        |
| --------------- | ---------------------------- |
| agent_id        | `report_generation_agent`    |
| capability      | `report_generation`          |
| category        | `reporting`                  |
| timeout_seconds | 240                          |

**Input schema:**

```json
{
  "title": "string (required)",
  "data": "dict (required). Structured data to include in report.",
  "report_type": "string enum: 'executive' | 'detailed' | 'analytics'. Default: 'executive'",
  "sections": "list[string] (optional). Requested section headings.",
  "include_visualizations": "boolean. Default: true"
}
```

**Output schema:**

```json
{
  "report_title": "string",
  "sections": [
    {"heading": "string", "content": "string", "data_refs": ["string"]}
  ],
  "executive_summary": "string",
  "visualizations": [
    {"type": "string", "title": "string", "data": "dict"}
  ]
}
```

---

## 9.7 Classification Agent

### Category Classification Agent

| Field           | Value                    |
| --------------- | ------------------------ |
| agent_id        | `classification_agent`   |
| capability      | `classification`         |
| category        | `classification`         |
| timeout_seconds | 60                       |

**Input schema:**

```json
{
  "text": "string (required). Text to classify.",
  "categories": "list[string] (required). Allowed categories.",
  "multi_label": "boolean. Default: false. If true, can assign multiple categories.",
  "min_confidence": "float. Default: 0.5"
}
```

**Output schema:**

```json
{
  "category": "string (top category)",
  "confidence": "float 0-1",
  "all_scores": [
    {"category": "string", "confidence": "float 0-1"}
  ]
}
```

---

# 10. Error Handling

## 10.1 Exception Hierarchy

```python
# src/platform/core/exceptions.py

class PlatformError(Exception):
    """Base exception for all platform errors."""
    retryable: bool = False

class AgentError(PlatformError):
    """Raised by agents during execution."""
    pass

class AgentTimeoutError(AgentError):
    """Agent exceeded its timeout_seconds."""
    retryable = True

class CapabilityNotFoundError(PlatformError):
    """No agent registered for the requested capability."""
    pass

class ToolError(PlatformError):
    """Error invoking an external tool."""
    retryable = True

class LLMError(PlatformError):
    """Error from LLM provider."""
    retryable = True

class LLMRateLimitError(LLMError):
    """Rate limited by LLM provider."""
    retryable = True

class ValidationError(PlatformError):
    """Input validation failure."""
    pass

class AuthenticationError(PlatformError):
    """Authentication/authorization failure."""
    pass
```

## 10.2 Error Handling Rules

1. **Agents must not catch generic `Exception` internally.** Let errors propagate to `BaseAgent.run()`.
2. **All LLM calls must have timeouts** (configured via `LLMRequest` or client defaults).
3. **Retryable errors** (LLM timeouts, rate limits, transient tool failures) are retried up to 3 times with exponential backoff (1s, 2s, 4s).
4. **Validation errors** return HTTP 400 immediately — no retry.
5. **Every error is logged** with correlation_id for tracing.
6. **API responses** always use the `ErrorDetail` schema (code + message + retryable).

---

# 11. Configuration

```python
# src/platform/config.py

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings. Loaded from environment variables."""

    # App
    app_name: str = "enterprise-ai-platform"
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Database
    database_url: str = "postgresql+asyncpg://user:pass@localhost:5432/platform"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # LLM
    llm_provider: str = "openai"            # "openai" | "anthropic" | "azure"
    llm_default_model: str = "gpt-4o"
    llm_api_key: str = ""
    llm_timeout_seconds: int = 60
    llm_max_retries: int = 3

    # Vector Store
    vector_store_type: str = "chroma"       # "chroma" | "pinecone"
    chroma_persist_dir: str = "./data/chroma"
    pinecone_api_key: str = ""
    pinecone_index: str = ""

    # Embedding
    embedding_model: str = "text-embedding-3-small"

    # Security
    jwt_secret: str = "change-me"
    api_key_header: str = "X-API-Key"
    cors_origins: list[str] = ["*"]

    # Observability
    otel_endpoint: str = ""
    enable_tracing: bool = True

    class Config:
        env_file = ".env"
        env_prefix = "PLATFORM_"
```

---

# 12. Observability

## 12.1 Structured Logging

All log entries must be JSON with these fields:

```json
{
  "timestamp": "ISO 8601",
  "level": "INFO | WARNING | ERROR",
  "correlation_id": "uuid",
  "agent_id": "string (if applicable)",
  "message": "string",
  "extra": {}
}
```

## 12.2 Tracing

Every agent execution creates a trace span. Trace spans are nested:

```
[task_span]
  └── [agent_span: summarization_agent]
        ├── [llm_call_span]
        └── [tool_call_span]
```

Use OpenTelemetry SDK. Export to Jaeger or OTLP collector.

## 12.3 Metrics (Prometheus)

| Metric                         | Type      | Labels                      |
| ------------------------------ | --------- | --------------------------- |
| `agent_executions_total`       | Counter   | agent_id, status            |
| `agent_execution_duration_ms`  | Histogram | agent_id                    |
| `llm_calls_total`              | Counter   | model, status               |
| `llm_call_duration_ms`         | Histogram | model                       |
| `tool_invocations_total`       | Counter   | tool_id, status             |
| `active_tasks`                 | Gauge     | —                           |

---

# 13. Security

## 13.1 Authentication

Support two modes (configurable):

1. **API Key** — passed in `X-API-Key` header. Validated against database.
2. **JWT** — Bearer token in `Authorization` header. Validated with `jwt_secret`.

## 13.2 RBAC Roles

| Role     | Permissions                                      |
| -------- | ------------------------------------------------ |
| admin    | All operations including agent/tool management   |
| operator | Execute agents, view tasks, view capabilities    |
| viewer   | Read-only: list capabilities, view task results  |

## 13.3 Audit Logging

Every API request and agent execution writes an audit log entry:

```json
{
  "timestamp": "ISO 8601",
  "user_id": "string",
  "action": "agent.execute | task.create | ...",
  "resource": "string",
  "result": "success | failure",
  "ip_address": "string"
}
```

---

# 14. Deployment

## 14.1 Docker Compose (Development)

```yaml
services:
  app:
    build: .
    ports: ["8000:8000"]
    env_file: .env
    depends_on: [postgres, redis]
    volumes: ["./data:/app/data"]

  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: platform
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    ports: ["5432:5432"]
    volumes: ["pgdata:/var/lib/postgresql/data"]

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]

volumes:
  pgdata:
```

## 14.2 Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY pyproject.toml .
RUN pip install --no-cache-dir .
COPY src/ src/
EXPOSE 8000
CMD ["uvicorn", "platform.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

# 15. Testing Strategy

## 15.1 Test Levels

| Level       | Scope                                         | Tools                 |
| ----------- | --------------------------------------------- | --------------------- |
| Unit        | Individual agents, registry, models            | pytest, unittest.mock |
| Integration | API endpoints, database, full agent execution  | pytest, httpx         |
| E2E         | Multi-step workflows through the API           | pytest, httpx         |

## 15.2 Testing Rules

1. **Every agent must have at least one unit test** that mocks the LLM and verifies output schema.
2. **LLM responses are mocked in unit tests.** Never call real LLM APIs in CI.
3. **Integration tests** use a test database (SQLite or test Postgres).
4. **All tests must pass before merge** (enforced by CI).

## 15.3 Example Unit Test Pattern

```python
# tests/unit/agents/test_summarization_agent.py

import pytest
from unittest.mock import AsyncMock
from platform.agents.unit.summarization_agent import SummarizationAgent
from platform.core.agent_context import AgentContext
from platform.models.domain import TaskInput


@pytest.fixture
def mock_context():
    ctx = AgentContext(
        llm=AsyncMock(),
        tools=AsyncMock(),
        knowledge=AsyncMock(),
    )
    ctx.llm.complete_json.return_value = {
        "summary": "Test summary.",
        "key_points": ["Point 1"],
        "original_length": 100,
        "summary_length": 10,
    }
    return ctx


@pytest.mark.asyncio
async def test_summarization_returns_valid_output(mock_context):
    agent = SummarizationAgent()
    task = TaskInput(capability="summarization", payload={"text": "Long text here..."})
    result = await agent.run(task, mock_context)

    assert result.status == "completed"
    assert "summary" in result.output
    assert isinstance(result.output["key_points"], list)
```

---

# 16. Implementation Order

Build the platform in this order. Each phase must be fully working before proceeding.

| Phase | Components                                                     | Deliverable                      |
| ----- | -------------------------------------------------------------- | -------------------------------- |
| 1     | Models, Config, Exceptions, BaseAgent, AgentContext             | Core framework compiles + tests  |
| 2     | CapabilityRegistry, LLMClient (mock)                           | Agent registration works         |
| 3     | First 3 unit agents: Summarization, Classification, Translation | Agents produce valid output      |
| 4     | FastAPI app, /v1/agents/execute, /v1/capabilities, /v1/health  | API serves requests              |
| 5     | CapabilityGraph, Orchestrator, /v1/tasks                       | Multi-step workflows work        |
| 6     | Remaining unit agents                                          | Full agent library               |
| 7     | Knowledge (vector store, retriever), Tool system               | RAG + tool calls work            |
| 8     | Security (auth, RBAC, audit), Middleware                       | Protected endpoints              |
| 9     | Observability (logging, tracing, metrics)                      | Full observability               |
| 10    | Docker, CI, E2E tests                                          | Production-ready deployment      |

---

# 17. Agent Capability Summary

| Category       | Agent                        | Capability Name          | agent_id                      |
| -------------- | ---------------------------- | ------------------------ | ----------------------------- |
| Research       | Deep Research                | `deep_research`          | `deep_research_agent`         |
| Research       | Web Search                   | `web_search`             | `web_search_agent`            |
| Document       | OCR                          | `ocr`                    | `ocr_agent`                   |
| Document       | Drafting                     | `document_drafting`      | `document_drafting_agent`     |
| Document       | Summarization                | `summarization`          | `summarization_agent`         |
| Document       | Comparison                   | `document_comparison`    | `document_comparison_agent`   |
| Document       | Proofreading                 | `proofreading`           | `proofreading_agent`          |
| Language       | Translation                  | `translation`            | `translation_agent`           |
| Language       | Keyword Extraction           | `keyword_extraction`     | `keyword_extraction_agent`    |
| Analytics      | Text-to-Analytics            | `text_to_analytics`      | `text_to_analytics_agent`     |
| Analytics      | Table Analysis               | `table_analysis`         | `table_analysis_agent`        |
| Analytics      | Statistical Analysis         | `statistical_analysis`   | `statistical_analysis_agent`  |
| Analytics      | Data Analysis                | `data_analysis`          | `data_analysis_agent`         |
| Code           | Code Generation              | `code_generation`        | `code_generation_agent`       |
| Code           | Code Refactoring             | `code_refactor`          | `code_refactor_agent`         |
| Reporting      | Report Generation            | `report_generation`      | `report_generation_agent`     |
| Classification | Category Classification      | `classification`         | `classification_agent`        |
