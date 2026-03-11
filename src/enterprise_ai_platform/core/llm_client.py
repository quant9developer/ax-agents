from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass

import httpx

from enterprise_ai_platform.config import Settings
from enterprise_ai_platform.core.exceptions import LLMError


@dataclass
class LLMRequest:
    messages: list[dict[str, object]]
    model: str = "gpt-4o"
    temperature: float = 0.2
    max_tokens: int = 4096
    response_format: dict[str, object] | None = None
    tools: list[dict[str, object]] | None = None


@dataclass
class LLMResponse:
    content: str
    model: str
    usage: dict[str, int]
    tool_calls: list[dict[str, object]] | None = None
    raw: dict[str, object] | None = None


class LLMClient:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings
        self.provider_name = settings.llm_provider if settings is not None else "mock"
        self.is_live = self._compute_is_live(settings)

    async def complete(self, request: LLMRequest) -> LLMResponse:
        if not self.is_live or self.settings is None:
            content = self._extract_prompt(request.messages)
            return LLMResponse(
                content=f"Mock response: {content[:200]}",
                model=request.model,
                usage={"prompt_tokens": 0, "completion_tokens": 0},
                raw={"mock": True},
            )

        return await self._complete_http(request)

    async def complete_json(self, request: LLMRequest, schema: dict[str, object]) -> dict[str, object]:
        response_format = request.response_format or {"type": "json_object"}
        raw = await self.complete(
            LLMRequest(
                messages=request.messages,
                model=request.model,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                response_format=response_format,
                tools=request.tools,
            )
        )
        parsed = self._parse_json_content(raw.content)
        if parsed is None:
            raise LLMError("Model did not return valid JSON content")
        _ = schema
        return parsed

    async def _complete_http(self, request: LLMRequest) -> LLMResponse:
        assert self.settings is not None
        attempt = 0
        last_error: Exception | None = None
        while attempt < max(1, self.settings.llm_max_retries):
            try:
                return await self._send_provider_request(request)
            except Exception as exc:
                last_error = exc
                attempt += 1
                if attempt >= max(1, self.settings.llm_max_retries):
                    break
                await asyncio.sleep(2 ** (attempt - 1))
        raise LLMError(f"LLM request failed: {last_error}") from last_error

    async def _send_provider_request(self, request: LLMRequest) -> LLMResponse:
        assert self.settings is not None
        provider = self.settings.llm_provider.lower()
        if provider in {"openai", "openai_compatible", "ollama", "vllm", "lmstudio"}:
            return await self._send_openai_compatible(request)
        if provider == "anthropic":
            return await self._send_anthropic(request)
        if provider == "gemini":
            return await self._send_gemini(request)
        raise LLMError(f"Unsupported LLM provider: {self.settings.llm_provider}")

    async def _send_openai_compatible(self, request: LLMRequest) -> LLMResponse:
        assert self.settings is not None
        payload: dict[str, object] = {
            "model": request.model or self.settings.llm_default_model,
            "messages": request.messages,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
        }
        if request.response_format is not None:
            payload["response_format"] = request.response_format
        if request.tools is not None:
            payload["tools"] = request.tools

        headers = {"Content-Type": "application/json"}
        if self.settings.llm_api_key:
            headers["Authorization"] = f"Bearer {self.settings.llm_api_key}"
        if self.settings.llm_organization:
            headers["OpenAI-Organization"] = self.settings.llm_organization

        async with httpx.AsyncClient(timeout=self.settings.llm_timeout_seconds) as client:
            response = await client.post(
                f"{self.settings.llm_base_url.rstrip('/')}/chat/completions",
                headers=headers,
                json=payload,
            )
        response.raise_for_status()
        body = response.json()
        choice = body["choices"][0]["message"]
        return LLMResponse(
            content=self._message_content_to_text(choice.get("content", "")),
            model=str(body.get("model", payload["model"])),
            usage=self._normalize_usage(body.get("usage", {})),
            tool_calls=choice.get("tool_calls"),
            raw=body,
        )

    async def _send_anthropic(self, request: LLMRequest) -> LLMResponse:
        assert self.settings is not None
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.settings.llm_api_key,
            "anthropic-version": "2023-06-01",
        }
        system, messages = self._split_system_messages(request.messages)
        payload: dict[str, object] = {
            "model": request.model or self.settings.llm_default_model,
            "messages": messages,
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
        }
        if system:
            payload["system"] = system

        async with httpx.AsyncClient(timeout=self.settings.llm_timeout_seconds) as client:
            response = await client.post(
                f"{self.settings.llm_base_url.rstrip('/')}/messages",
                headers=headers,
                json=payload,
            )
        response.raise_for_status()
        body = response.json()
        content_blocks = body.get("content", [])
        text = "\n".join(
            str(block.get("text", ""))
            for block in content_blocks
            if isinstance(block, dict) and block.get("type") == "text"
        )
        return LLMResponse(
            content=text,
            model=str(body.get("model", payload["model"])),
            usage={
                "prompt_tokens": int(body.get("usage", {}).get("input_tokens", 0)),
                "completion_tokens": int(body.get("usage", {}).get("output_tokens", 0)),
            },
            raw=body,
        )

    async def _send_gemini(self, request: LLMRequest) -> LLMResponse:
        assert self.settings is not None
        headers = {"Content-Type": "application/json"}
        model = request.model or self.settings.llm_default_model
        payload = {
            "contents": self._to_gemini_contents(request.messages),
            "generationConfig": {
                "temperature": request.temperature,
                "maxOutputTokens": request.max_tokens,
                "responseMimeType": "application/json"
                if request.response_format is not None
                else "text/plain",
            },
        }
        endpoint = (
            f"{self.settings.llm_base_url.rstrip('/')}/models/{model}:generateContent"
            f"?key={self.settings.llm_api_key}"
        )
        async with httpx.AsyncClient(timeout=self.settings.llm_timeout_seconds) as client:
            response = await client.post(endpoint, headers=headers, json=payload)
        response.raise_for_status()
        body = response.json()
        candidates = body.get("candidates", [])
        parts = []
        if candidates:
            content = candidates[0].get("content", {})
            parts = content.get("parts", [])
        text = "\n".join(
            str(part.get("text", "")) for part in parts if isinstance(part, dict) and "text" in part
        )
        usage = body.get("usageMetadata", {})
        return LLMResponse(
            content=text,
            model=model,
            usage={
                "prompt_tokens": int(usage.get("promptTokenCount", 0)),
                "completion_tokens": int(usage.get("candidatesTokenCount", 0)),
            },
            raw=body,
        )

    def provider_info(self) -> dict[str, object]:
        if self.settings is None:
            return {"provider": "mock", "model": "mock", "live": False}
        return {
            "provider": self.settings.llm_provider,
            "model": self.settings.llm_default_model,
            "base_url": self.settings.llm_base_url,
            "live": self.is_live,
            "api_key_configured": bool(self.settings.llm_api_key),
            "supported_providers": ["openai", "openai_compatible", "anthropic", "gemini"],
        }

    @staticmethod
    def _compute_is_live(settings: Settings | None) -> bool:
        if settings is None or not settings.llm_base_url:
            return False
        provider = settings.llm_provider.lower()
        if provider in {"openai_compatible", "ollama", "vllm", "lmstudio"}:
            return True
        return bool(settings.llm_api_key)

    @staticmethod
    def _normalize_usage(usage: object) -> dict[str, int]:
        if not isinstance(usage, dict):
            return {"prompt_tokens": 0, "completion_tokens": 0}
        return {
            "prompt_tokens": int(usage.get("prompt_tokens", 0)),
            "completion_tokens": int(usage.get("completion_tokens", 0)),
        }

    @staticmethod
    def _message_content_to_text(content: object) -> str:
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts: list[str] = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    parts.append(str(item.get("text", "")))
            return "\n".join(part for part in parts if part)
        return str(content)

    @staticmethod
    def _split_system_messages(
        messages: list[dict[str, object]],
    ) -> tuple[str, list[dict[str, object]]]:
        system_parts: list[str] = []
        output_messages: list[dict[str, object]] = []
        for message in messages:
            role = str(message.get("role", "user"))
            content = str(message.get("content", ""))
            if role == "system":
                system_parts.append(content)
            else:
                output_messages.append({"role": role, "content": content})
        return ("\n\n".join(system_parts), output_messages)

    @staticmethod
    def _to_gemini_contents(messages: list[dict[str, object]]) -> list[dict[str, object]]:
        contents: list[dict[str, object]] = []
        for message in messages:
            role = str(message.get("role", "user"))
            gemini_role = "model" if role == "assistant" else "user"
            contents.append({"role": gemini_role, "parts": [{"text": str(message.get("content", ""))}]})
        return contents

    @staticmethod
    def _parse_json_content(content: str) -> dict[str, object] | None:
        try:
            parsed = json.loads(content)
            return parsed if isinstance(parsed, dict) else None
        except json.JSONDecodeError:
            pass

        if "```json" in content:
            fenced = content.split("```json", maxsplit=1)[1].split("```", maxsplit=1)[0].strip()
            try:
                parsed = json.loads(fenced)
                return parsed if isinstance(parsed, dict) else None
            except json.JSONDecodeError:
                return None

        start = content.find("{")
        end = content.rfind("}")
        if start != -1 and end != -1 and end > start:
            candidate = content[start : end + 1]
            try:
                parsed = json.loads(candidate)
                return parsed if isinstance(parsed, dict) else None
            except json.JSONDecodeError:
                return None
        return None

    @staticmethod
    def _extract_prompt(messages: list[dict[str, object]]) -> str:
        if not messages:
            return ""
        last = messages[-1]
        content = last.get("content", "")
        return str(content)
