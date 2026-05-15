"""Record memory reads/writes when a pipeline RunCollector is active."""

from __future__ import annotations

from typing import Any, Literal

from aiuthor.observability.context import get_collector, get_current_agent, utc_iso

Direction = Literal["read", "write"]


def log_memory_io(
    direction: Direction,
    store: str,
    detail: str,
    *,
    agent: str | None = None,
    extra: dict[str, Any] | None = None,
) -> None:
    coll = get_collector()
    if coll is None:
        return
    coll.memory_io.append(
        {
            "ts": utc_iso(),
            "agent": agent or get_current_agent(),
            "direction": direction,
            "store": store,
            "detail": detail[:2000],
            "extra": extra or {},
        }
    )
