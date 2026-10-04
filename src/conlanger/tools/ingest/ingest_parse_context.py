"""Active ingest parse-pass name (ContextVar); no imports from other ingest modules."""

from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager
from contextvars import ContextVar

_ingest_parse_pass: ContextVar[str | None] = ContextVar(
    "ingest_parse_pass", default=None
)


def current_ingest_parse_pass() -> str | None:
    return _ingest_parse_pass.get()


@contextmanager
def ingest_parse_pass(name: str) -> Generator[None, None, None]:
    token = _ingest_parse_pass.set(name)
    try:
        yield
    finally:
        _ingest_parse_pass.reset(token)
