# Enterprise AI Agent Platform

Production-oriented FastAPI platform for executing modular AI agents by capability.

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
uvicorn enterprise_ai_platform.main:app --host 0.0.0.0 --port 8088 --reload
```

## LLM Backends

The platform supports these provider modes:

- `openai`
- `openai_compatible`
- `anthropic`
- `gemini`

Set these environment variables:

```bash
PLATFORM_LLM_PROVIDER=openai
PLATFORM_LLM_BASE_URL=https://api.openai.com/v1
PLATFORM_LLM_API_KEY=...
PLATFORM_LLM_DEFAULT_MODEL=gpt-4o
```

Examples:

```bash
# OpenAI
PLATFORM_LLM_PROVIDER=openai
PLATFORM_LLM_BASE_URL=https://api.openai.com/v1
PLATFORM_LLM_DEFAULT_MODEL=gpt-4o

# Claude
PLATFORM_LLM_PROVIDER=anthropic
PLATFORM_LLM_BASE_URL=https://api.anthropic.com/v1
PLATFORM_LLM_DEFAULT_MODEL=claude-3-5-sonnet-latest

# Gemini
PLATFORM_LLM_PROVIDER=gemini
PLATFORM_LLM_BASE_URL=https://generativelanguage.googleapis.com/v1beta
PLATFORM_LLM_DEFAULT_MODEL=gemini-2.0-flash

# Local / open source model server
PLATFORM_LLM_PROVIDER=openai_compatible
PLATFORM_LLM_BASE_URL=http://localhost:8088/v1
PLATFORM_LLM_DEFAULT_MODEL=meta-llama/Meta-Llama-3.1-8B-Instruct
```

For local or open source model servers, point `PLATFORM_LLM_BASE_URL` at any OpenAI-compatible endpoint such as vLLM.

## Demo Flow

Useful endpoints for a live demo:

- `GET /v1/health`
- `GET /v1/demo/providers`
- `GET /v1/demo/scenarios`
- `GET /v1/capabilities`
- `POST /v1/agents/execute`

Typical sequence:

```bash
curl -H "X-API-Key: dev-key" http://localhost:8088/v1/demo/providers
curl -H "X-API-Key: dev-key" http://localhost:8088/v1/demo/scenarios
curl -H "X-API-Key: dev-key" -H "Content-Type: application/json" \
  -d '{"capability":"summarization","payload":{"text":"Quarterly revenue grew 18 percent year over year while margin improved two points.","max_length":80}}' \
  http://localhost:8088/v1/agents/execute
```

## API

- `POST /v1/agents/execute`
- `POST /v1/tasks`
- `GET /v1/a2a/agents`
- `POST /v1/a2a/invoke`
- `GET /v1/capabilities`
- `GET /v1/health`

## MCP and A2A

This project now includes first-cut support for both MCP and A2A.

- `MCP`
  - exposed through the `mcp` tool connector
  - configured via `PLATFORM_MCP_SERVERS`
  - invocation shape: `server + tool + arguments`
  - current concrete use case: `deep_research` can call the `browser` MCP server to gather web evidence before synthesizing results with the LLM
  - current concrete use case: `summarization` can call the `filesystem` MCP server to read a local document before summarizing it
- `A2A`
  - exposed through `GET /v1/a2a/agents` and `POST /v1/a2a/invoke`
  - lets one agent-facing caller invoke another agent explicitly through a structured protocol

Example MCP configuration:

```bash
PLATFORM_MCP_SERVERS={"browser":"http://127.0.0.1:17002","filesystem":"http://127.0.0.1:17001"}
```

Example MCP-backed research flow:

```bash
curl -X POST http://localhost:8088/v1/agents/execute \
  -H "X-API-Key: dev-key" \
  -H "Content-Type: application/json" \
  -d '{
    "capability": "deep_research",
    "payload": {
      "topic": "한국 리테일 산업의 AI 에이전트 도입 사례",
      "depth": "comprehensive",
      "sources_limit": 5
    }
  }'
```

If the `browser` MCP server is configured, the agent first calls MCP `browser.search`, then synthesizes those findings with the LLM. If MCP is unavailable, it falls back to local evidence and still returns a result.

The `deep_research` result now includes an explicit `sources` array with source title, URL, and snippet so the research output can be presented with citations.
On the `/demo` page, those sources are rendered as clickable links under the result panel for the `deep_research` scenario.

The `summarization` capability can also use MCP `filesystem.read_text` when you provide `file_path`. The demo includes a `로컬 문서 요약` scenario that reads `examples/demo/quarterly_update_ko.txt`.

MCP status is exposed in `GET /v1/demo/protocols` with three distinct states:

- connector registered: the platform has the MCP tool enabled
- configured: `PLATFORM_MCP_SERVERS` contains one or more MCP endpoints
- reachable: the configured MCP endpoint responds over HTTP

This distinction matters because a registered connector does not mean a real MCP backend is running.

You can also trigger the same MCP browser-search path used by `deep_research` through:

- `POST /v1/demo/mcp/test`

The `/demo` page exposes this as the `MCP 연결 테스트` button, with a selector for both `browser.search` and `filesystem.read_text`.

### Local MCP Bridges

This repo includes lightweight local MCP bridges:

```bash
source .venv/bin/activate
PYTHONPATH=src uvicorn enterprise_ai_platform.mcp.filesystem_bridge:app --host 127.0.0.1 --port 17001
PYTHONPATH=src uvicorn enterprise_ai_platform.mcp.browser_bridge:app --host 127.0.0.1 --port 17002
```

Then restart the main app so it picks up `PLATFORM_MCP_SERVERS`.

Filesystem verification:

```bash
curl http://127.0.0.1:17001/health
curl -X POST http://127.0.0.1:17001/invoke \
  -H "Content-Type: application/json" \
  -d '{"tool":"read_text","arguments":{"path":"examples/demo/quarterly_update_ko.txt"}}'
```

Quick verification:

```bash
curl http://127.0.0.1:17002/health
curl -X POST http://127.0.0.1:17002/invoke \
  -H "Content-Type: application/json" \
  -d '{"tool":"search","arguments":{"query":"ai agents","limit":3}}'
```

Example A2A call:

```bash
curl -X POST http://localhost:8088/v1/a2a/invoke \
  -H "X-API-Key: dev-key" \
  -H "Content-Type: application/json" \
  -d '{
    "sender_agent_id": "external",
    "receiver_agent_id": "summarization_agent",
    "capability": "summarization",
    "payload": {
      "text": "긴 문서를 요약해 주세요.",
      "max_length": 100
    }
  }'
```

## External Integration

Other systems should integrate with this platform through its HTTP API.

- Use `POST /v1/agents/execute` when the caller already knows the capability to invoke.
- Use `POST /v1/tasks` when the caller wants the platform to build and run a multi-step workflow.

Example: single capability call

```bash
curl -X POST http://localhost:8088/v1/agents/execute \
  -H "X-API-Key: dev-key" \
  -H "Content-Type: application/json" \
  -d '{
    "capability": "summarization",
    "payload": {
      "text": "긴 문서 내용...",
      "max_length": 120
    }
  }'
```

Example: workflow-style call

```bash
curl -X POST http://localhost:8088/v1/tasks \
  -H "X-API-Key: dev-key" \
  -H "Content-Type: application/json" \
  -d '{
    "request": "지난 분기 매출 데이터를 분석하고 경영진용 보고서를 생성해줘",
    "payload": {
      "data_source": "quarterly_sales",
      "quarter": "2025-Q4"
    }
  }'
```

Example: Python client

```python
import httpx

BASE_URL = "http://localhost:8088"
API_KEY = "dev-key"

payload = {
    "capability": "translation",
    "payload": {
        "text": "안녕하세요. 기다려 주셔서 감사합니다.",
        "source_language": "ko",
        "target_language": "en",
    },
}

with httpx.Client(base_url=BASE_URL, timeout=60.0) as client:
    response = client.post(
        "/v1/agents/execute",
        headers={"X-API-Key": API_KEY},
        json=payload,
    )
    response.raise_for_status()
    result = response.json()

print(result)
```

### When To Use API vs A2A

- Use the standard API for most integrations.
  - caller is a web app, backend service, batch job, or external product
  - preferred endpoints: `POST /v1/agents/execute` or `POST /v1/tasks`
- Use A2A when the caller is itself acting as an agent or agent platform.
  - caller wants explicit sender and receiver agent identity
  - preferred endpoint: `POST /v1/a2a/invoke`

Side-by-side:

- API
  - "Call the `summarization` capability and give me the result."
- A2A
  - "Agent `external_research_coordinator` is invoking `summarization_agent` for the `summarization` capability."
