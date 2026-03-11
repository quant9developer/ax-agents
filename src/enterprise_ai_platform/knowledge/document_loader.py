from __future__ import annotations

from pathlib import Path


class DocumentLoader:
    def load_text(self, file_path: str) -> str:
        return Path(file_path).read_text(encoding="utf-8")
