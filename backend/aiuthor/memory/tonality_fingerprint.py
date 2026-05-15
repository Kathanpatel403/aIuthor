"""Tonality fingerprint per surface (embeddings optional until Phase 4)."""

from __future__ import annotations

from aiuthor.memory.schemas import TonalitySurfaceRecord
from aiuthor.memory.store import BookMemoryState, get_memory_store


class TonalityFingerprint:
    def __init__(self, book_id: str) -> None:
        self._book_id = book_id
        self._store = get_memory_store()

    def _state(self) -> BookMemoryState:
        return self._store.get_or_create(self._book_id)

    def set_surface(self, record: TonalitySurfaceRecord) -> TonalitySurfaceRecord:
        st = self._state()
        with self._store._lock:
            st.tonality[record.surface] = record
        return record

    def get_surface(self, surface: str) -> TonalitySurfaceRecord | None:
        st = self._state()
        with self._store._lock:
            return st.tonality.get(surface)

    def all_surfaces(self) -> dict[str, TonalitySurfaceRecord]:
        st = self._state()
        with self._store._lock:
            return dict(st.tonality)
