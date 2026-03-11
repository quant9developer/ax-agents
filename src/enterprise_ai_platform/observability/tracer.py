from __future__ import annotations

from contextlib import contextmanager


@contextmanager
def trace_span(name: str):
    _ = name
    yield
