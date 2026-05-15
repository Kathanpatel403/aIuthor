"""Callback index — cross-chapter continuity; supports repair after chapter insert."""

from __future__ import annotations

import uuid
from typing import Literal

from aiuthor.memory.schemas import CallbackRecord
from aiuthor.memory.store import BookMemoryState, get_memory_store
from aiuthor.observability.memory_audit import log_memory_io

CallbackKind = Literal["echo", "foreshadow", "payoff", "motif"]


class CallbackIndex:
    def __init__(self, book_id: str) -> None:
        self._book_id = book_id
        self._store = get_memory_store()

    def _state(self) -> BookMemoryState:
        return self._store.get_or_create(self._book_id)

    def append(self, callback: CallbackRecord) -> None:
        st = self._state()
        with self._store._lock:
            st.callbacks.append(callback)
        log_memory_io(
            "write",
            "callback_index",
            f"append from={callback.from_chapter} to={callback.to_chapter}",
        )

    def add_callback(
        self,
        *,
        from_chapter: int,
        to_chapter: int,
        snippet: str,
        kind: CallbackKind = "echo",
    ) -> CallbackRecord:
        rec = CallbackRecord(
            id=str(uuid.uuid4()),
            from_chapter=from_chapter,
            to_chapter=to_chapter,
            kind=kind,
            snippet=snippet.strip(),
        )
        self.append(rec)
        return rec

    def list_all(self) -> list[CallbackRecord]:
        st = self._state()
        with self._store._lock:
            n = len(st.callbacks)
            rows = list(st.callbacks)
        log_memory_io("read", "callback_index", f"list_all count={n}")
        return rows

    def shift_chapters_after_insert(self, insert_after_chapter: int) -> int:
        """
        Renumber any chapter reference strictly after the insertion gap.
        """
        st = self._state()
        touched = 0
        with self._store._lock:
            for cb in st.callbacks:
                if cb.from_chapter > insert_after_chapter:
                    cb.from_chapter += 1
                    touched += 1
                if cb.to_chapter > insert_after_chapter:
                    cb.to_chapter += 1
                    touched += 1
        return touched

    def trigger_repair_after_chapter_insert(self, insert_after_chapter: int) -> int:
        """
        Public hook for orchestrator / Test D: same as shift; name documents contract.
        """
        return self.shift_chapters_after_insert(insert_after_chapter)
