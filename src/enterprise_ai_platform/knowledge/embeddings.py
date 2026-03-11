from __future__ import annotations


class Embeddings:
    def embed(self, text: str) -> list[float]:
        return [float((ord(ch) % 10) / 10.0) for ch in text[:32]]
