from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class VectorStore:
    documents: list[dict[str, object]] = field(default_factory=list)

    def add(self, item: dict[str, object]) -> None:
        self.documents.append(item)

    def search(self, query: str, top_k: int = 5) -> list[dict[str, object]]:
        lower = query.lower()
        scored = [doc for doc in self.documents if lower in str(doc).lower()]
        return scored[:top_k]
