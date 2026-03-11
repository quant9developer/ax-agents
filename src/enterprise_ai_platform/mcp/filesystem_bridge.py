from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


WORKSPACE_ROOT = Path.cwd()


class MCPInvokeRequest(BaseModel):
    tool: str
    arguments: dict[str, object] = Field(default_factory=dict)


def _resolve_path(raw_path: str) -> Path:
    candidate = Path(raw_path).expanduser()
    if not candidate.is_absolute():
        candidate = (WORKSPACE_ROOT / candidate).resolve()
    else:
        candidate = candidate.resolve()
    if WORKSPACE_ROOT not in candidate.parents and candidate != WORKSPACE_ROOT:
        raise HTTPException(status_code=403, detail="path is outside the workspace root")
    return candidate


app = FastAPI(title="filesystem-mcp-bridge", version="1.0.0")


@app.get("/")
def root() -> dict[str, object]:
    return {"service": "filesystem-mcp-bridge", "status": "ok", "tools": ["read_text", "list_files"]}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/invoke")
async def invoke(request: MCPInvokeRequest) -> dict[str, object]:
    if request.tool == "read_text":
        raw_path = str(request.arguments.get("path", "")).strip()
        if not raw_path:
            raise HTTPException(status_code=400, detail="read_text requires path")
        file_path = _resolve_path(raw_path)
        if not file_path.exists() or not file_path.is_file():
            raise HTTPException(status_code=404, detail="file not found")
        content = file_path.read_text(encoding="utf-8")
        return {
            "tool": "read_text",
            "path": str(file_path),
            "content": content,
        }

    if request.tool == "list_files":
        raw_path = str(request.arguments.get("path", ".")).strip() or "."
        limit = max(1, min(100, int(request.arguments.get("limit", 20))))
        dir_path = _resolve_path(raw_path)
        if not dir_path.exists() or not dir_path.is_dir():
            raise HTTPException(status_code=404, detail="directory not found")
        items = [
            {
                "name": child.name,
                "path": str(child),
                "type": "directory" if child.is_dir() else "file",
            }
            for child in sorted(dir_path.iterdir())[:limit]
        ]
        return {
            "tool": "list_files",
            "path": str(dir_path),
            "items": items,
        }

    raise HTTPException(status_code=400, detail=f"Unsupported tool: {request.tool}")
