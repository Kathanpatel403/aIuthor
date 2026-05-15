"""Agent-level spans (timing events)."""

from __future__ import annotations

import logging
import time
from collections.abc import Generator
from contextlib import contextmanager

from aiuthor.observability.context import get_collector, get_current_agent, utc_iso

logger = logging.getLogger(__name__)


@contextmanager
def trace_span(step: str, extra: dict | None = None) -> Generator[None, None, None]:
    coll = get_collector()
    t0 = time.perf_counter()
    evt = {"ts": utc_iso(), "step": step, "agent": get_current_agent(), "phase": "start"}
    if extra:
        evt["extra"] = extra
    if coll is not None:
        coll.trace_events.append(evt)
    try:
        yield
    finally:
        dt_ms = round((time.perf_counter() - t0) * 1000, 2)
        done = {
            "ts": utc_iso(),
            "step": step,
            "agent": get_current_agent(),
            "phase": "end",
            "duration_ms": dt_ms,
        }
        if coll is not None:
            coll.trace_events.append(done)
