"""Append-only decision log for planner / memory-keeper auditing."""

from __future__ import annotations

import uuid
from typing import Any

from aiuthor.memory.schemas import DecisionLogEntry
from aiuthor.memory.store import BookMemoryState, get_memory_store


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
            return list(st.decisions)
