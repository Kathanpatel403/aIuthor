"""Append-only decision log for planner / memory-keeper auditing."""

from __future__ import annotations

import uuid
from typing import Any

from aiuthor.memory.schemas import DecisionLogEntry
from aiuthor.memory.store import BookMemoryState, get_memory_store
from aiuthor.observability.memory_audit import log_memory_io


class DecisionLog:
    def __init__(self, book_id: str) -> None:
        self._book_id = book_id
        self._store = get_memory_store()

    def _state(self) -> BookMemoryState:
        return self._store.get_or_create(self._book_id)

    def append(self, entry: DecisionLogEntry) -> DecisionLogEntry:
        st = self._state()
        with self._store._lock:
            st.decisions.append(entry)
        log_memory_io("write", "decision_log", f"append action={entry.action} agent={entry.agent}")
        return entry

    def append_event(self, *, agent: str, action: str, details: dict[str, Any] | None = None) -> DecisionLogEntry:
        entry = DecisionLogEntry(
            id=str(uuid.uuid4()),
            agent=agent,
            action=action,
            details=dict(details or {}),
        )
        return self.append(entry)

    def list_all(self) -> list[DecisionLogEntry]:
        st = self._state()
        with self._store._lock:
            n = len(st.decisions)
            rows = list(st.decisions)
        log_memory_io("read", "decision_log", f"list_all count={n}")
        return rows
