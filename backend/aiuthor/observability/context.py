"""Per-request / per-pipeline run context (async-safe via contextvars)."""

from __future__ import annotations

import uuid
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Generator

_current_agent: ContextVar[str] = ContextVar("current_agent", default="pipeline")
_collector: ContextVar["RunCollector | None"] = ContextVar("collector", default=None)


def utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class RunCollector:
    """Accumulates observability for one pipeline run."""

    run_id: str
    book_id: str
    started_at: str = field(default_factory=utc_iso)
    trace_events: list[dict[str, Any]] = field(default_factory=list)
    prompts: list[dict[str, Any]] = field(default_factory=list)
    memory_io: list[dict[str, Any]] = field(default_factory=list)
    ledger: list[dict[str, Any]] = field(default_factory=list)


def get_collector() -> RunCollector | None:
    return _collector.get()


def set_collector(c: RunCollector | None) -> None:
    _collector.set(c)


def get_current_agent() -> str:
    return _current_agent.get()


def set_current_agent(name: str) -> None:
    _current_agent.set(name)


def new_run_id() -> str:
    return str(uuid.uuid4())


@contextmanager
def pipeline_run_context(book_id: str, run_id: str | None = None) -> Generator[RunCollector, None, None]:
    rid = run_id or book_id
    coll = RunCollector(run_id=rid, book_id=book_id)
    token_c = _collector.set(coll)
    token_a = _current_agent.set("pipeline")
    try:
        yield coll
    finally:
        _current_agent.reset(token_a)
        _collector.reset(token_c)
