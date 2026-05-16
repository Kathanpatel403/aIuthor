"""Tonality fingerprint per surface (embeddings optional until Phase 4)."""

from __future__ import annotations

from aiuthor.memory.schemas import TonalitySurfaceRecord
from aiuthor.memory.store import BookMemoryState, get_memory_store
from aiuthor.observability.memory_audit import log_memory_io


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
        log_memory_io("write", "tonality_fingerprint", f"surface={record.surface}")
        self._store.touch_persist(self._book_id)
        return record

    def get_surface(self, surface: str) -> TonalitySurfaceRecord | None:
        st = self._state()
        with self._store._lock:
            row = st.tonality.get(surface)
        log_memory_io("read", "tonality_fingerprint", f"get_surface={surface!r} hit={row is not None}")
        return row

    def all_surfaces(self) -> dict[str, TonalitySurfaceRecord]:
        st = self._state()
        with self._store._lock:
            d = dict(st.tonality)
        log_memory_io("read", "tonality_fingerprint", f"all_surfaces count={len(d)}")
        return d
