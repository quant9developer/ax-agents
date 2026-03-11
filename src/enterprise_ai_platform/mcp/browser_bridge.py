from __future__ import annotations

from html import unescape
from urllib.parse import parse_qs, quote_plus, urlparse
import re

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


SEARCH_URL = "https://duckduckgo.com/html/"
TAG_RE = re.compile(r"<[^>]+>")
RESULT_LINK_RE = re.compile(
    r'<a[^>]*class="result__a"[^>]*href="(?P<href>[^"]+)"[^>]*>(?P<title>.*?)</a>',
    re.IGNORECASE | re.DOTALL,
)


class MCPInvokeRequest(BaseModel):
    tool: str
    arguments: dict[str, object] = Field(default_factory=dict)


def _clean_html(text: str) -> str:
    collapsed = TAG_RE.sub(" ", unescape(text))
    return " ".join(collapsed.split())


def _extract_target_url(href: str) -> str:
    parsed = urlparse(href)
    if parsed.netloc.endswith("duckduckgo.com") and parsed.path.startswith("/l/"):
        uddg = parse_qs(parsed.query).get("uddg", [])
        if uddg:
            return unescape(uddg[0])
    if href.startswith("//"):
        return f"https:{href}"
    return unescape(href)


def parse_duckduckgo_results(html: str, *, limit: int) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    for match in RESULT_LINK_RE.finditer(html):
        title = _clean_html(match.group("title"))
        href = _extract_target_url(match.group("href"))
        trailing = html[match.end() : match.end() + 1200]
        snippet_match = re.search(r'<a[^>]*class="result__snippet"[^>]*>(.*?)</a>', trailing, re.IGNORECASE | re.DOTALL)
        if snippet_match is None:
            snippet_match = re.search(r'<div[^>]*class="result__snippet"[^>]*>(.*?)</div>', trailing, re.IGNORECASE | re.DOTALL)
        snippet = _clean_html(snippet_match.group(1)) if snippet_match is not None else ""
        if not title:
            continue
        items.append({"title": title, "url": href, "snippet": snippet})
        if len(items) >= limit:
            break
    return items


async def search(query: str, *, limit: int = 5) -> list[dict[str, str]]:
    url = f"{SEARCH_URL}?q={quote_plus(query)}"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
    }
    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
        response = await client.get(url, headers=headers)
    response.raise_for_status()
    return parse_duckduckgo_results(response.text, limit=limit)


app = FastAPI(title="browser-mcp-bridge", version="1.0.0")


@app.get("/")
def root() -> dict[str, object]:
    return {"service": "browser-mcp-bridge", "status": "ok", "tools": ["search"]}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/invoke")
async def invoke(request: MCPInvokeRequest) -> dict[str, object]:
    if request.tool != "search":
        raise HTTPException(status_code=400, detail=f"Unsupported tool: {request.tool}")

    query = str(request.arguments.get("query", "")).strip()
    limit = max(1, min(10, int(request.arguments.get("limit", 5))))
    if not query:
        raise HTTPException(status_code=400, detail="search requires a non-empty query")

    try:
        items = await search(query, limit=limit)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"search failed: {exc}") from exc

    return {"tool": "search", "query": query, "items": items}
