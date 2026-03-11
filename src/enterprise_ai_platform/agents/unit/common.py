from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Sequence
import math
import re
import time

from enterprise_ai_platform.core.agent_context import AgentContext
from enterprise_ai_platform.core.base_agent import BaseAgent
from enterprise_ai_platform.core.exceptions import LLMError
from enterprise_ai_platform.core.llm_client import LLMRequest
from enterprise_ai_platform.models.domain import (
    AgentCategory,
    AgentMetadata,
    CapabilityDescriptor,
    TaskInput,
)

WORD_RE = re.compile(r"[A-Za-z0-9']+")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "has",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "to",
    "was",
    "were",
    "with",
}
HANGUL_RE = re.compile(r"[\uac00-\ud7a3]")


class JSONEchoAgent(BaseAgent):
    capability_name: str = ""
    agent_id: str = ""
    name: str = ""
    description: str = ""
    category: AgentCategory = AgentCategory.DOCUMENT
    timeout_seconds: int = 120
    input_schema: dict[str, object] = {"type": "object"}
    output_schema: dict[str, object] = {"type": "object"}

    def metadata(self) -> AgentMetadata:
        return AgentMetadata(
            agent_id=self.agent_id,
            name=self.name,
            description=self.description,
            category=self.category,
            timeout_seconds=self.timeout_seconds,
            capabilities=[
                CapabilityDescriptor(
                    name=self.capability_name,
                    description=self.description,
                    input_schema=self.input_schema,
                    output_schema=self.output_schema,
                    category=self.category,
                )
            ],
        )

    async def execute(self, task: TaskInput, context: AgentContext) -> dict[str, object]:
        _ = context
        return {"capability": self.capability_name, "input": task.payload}


def trace(context: AgentContext, action: str, input_summary: str, output_summary: str) -> None:
    started = time.perf_counter()
    duration_ms = max(1, int((time.perf_counter() - started) * 1000))
    context.add_trace(
        step=len(context.traces) + 1,
        action=action,
        input_summary=input_summary,
        output_summary=output_summary,
        duration_ms=duration_ms,
    )


def words(text: str) -> list[str]:
    return WORD_RE.findall(text.lower())


def split_sentences(text: str) -> list[str]:
    chunks = [chunk.strip() for chunk in SENTENCE_SPLIT_RE.split(text.strip()) if chunk.strip()]
    return chunks if chunks else ([text.strip()] if text.strip() else [])


def top_keywords(text: str, limit: int = 10) -> list[tuple[str, int]]:
    counts = Counter(word for word in words(text) if len(word) > 2 and word not in STOPWORDS)
    return counts.most_common(limit)


def sentence_scores(text: str) -> list[tuple[str, int]]:
    ranked: list[tuple[str, int]] = []
    keywords = dict(top_keywords(text, limit=20))
    for sentence in split_sentences(text):
        score = sum(keywords.get(token, 0) for token in words(sentence))
        ranked.append((sentence, score))
    return ranked


def summarize_text(text: str, max_words: int = 120) -> tuple[str, list[str]]:
    ranked = sentence_scores(text)
    ranked.sort(key=lambda item: item[1], reverse=True)
    selected = [sentence for sentence, _score in ranked[:3]]
    if not selected:
        return ("", [])
    summary = " ".join(selected)
    summary_tokens = summary.split()
    if len(summary_tokens) > max_words:
        summary = " ".join(summary_tokens[:max_words])
    key_points = selected[:3]
    return (summary.strip(), key_points)


def normalize_rows(data: object) -> list[dict[str, object]]:
    if isinstance(data, list):
        return [row for row in data if isinstance(row, dict)]
    return []


def numeric_columns(rows: Sequence[dict[str, object]]) -> dict[str, list[float]]:
    columns: dict[str, list[float]] = {}
    for row in rows:
        for key, value in row.items():
            if isinstance(value, bool):
                continue
            if isinstance(value, int | float):
                columns.setdefault(key, []).append(float(value))
                continue
            if isinstance(value, str):
                try:
                    columns.setdefault(key, []).append(float(value))
                except ValueError:
                    continue
    return columns


def basic_stats(values: Sequence[float]) -> dict[str, float]:
    if not values:
        return {"mean": 0.0, "median": 0.0, "std": 0.0, "min": 0.0, "max": 0.0}
    ordered = sorted(values)
    length = len(ordered)
    mean = sum(ordered) / length
    midpoint = length // 2
    median = ordered[midpoint] if length % 2 else (ordered[midpoint - 1] + ordered[midpoint]) / 2
    variance = sum((value - mean) ** 2 for value in ordered) / length
    return {
        "mean": round(mean, 4),
        "median": round(median, 4),
        "std": round(math.sqrt(variance), 4),
        "min": round(min(ordered), 4),
        "max": round(max(ordered), 4),
    }


def trend(values: Sequence[float]) -> str:
    if len(values) < 2:
        return "stable"
    if values[-1] > values[0]:
        return "increasing"
    if values[-1] < values[0]:
        return "decreasing"
    return "stable"


def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def unique_preserve_order(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            output.append(value)
    return output


def infer_output_language(*texts: str, requested: str | None = None, default: str = "en") -> str:
    normalized_requested = (requested or "").strip().lower()
    if normalized_requested:
        return normalized_requested
    if any(HANGUL_RE.search(text or "") for text in texts):
        return "ko"
    return default


def llm_enabled(context: AgentContext) -> bool:
    return bool(getattr(context.llm, "is_live", False))


async def try_complete_json(
    context: AgentContext,
    *,
    system_prompt: str,
    user_prompt: str,
    schema: dict[str, object],
    model: str | None = None,
    temperature: float = 0.2,
    max_tokens: int = 1500,
) -> dict[str, object] | None:
    if not llm_enabled(context):
        return None

    try:
        return await context.llm.complete_json(
            LLMRequest(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                model=model or "gpt-4o",
                temperature=temperature,
                max_tokens=max_tokens,
            ),
            schema=schema,
        )
    except LLMError:
        return None
