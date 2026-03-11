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
- `GET /v1/capabilities`
- `GET /v1/health`

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
