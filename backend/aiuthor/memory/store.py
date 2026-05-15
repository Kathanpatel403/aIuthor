"""Process-local in-memory book store (Redis-swappable interface)."""

from __future__ import annotations

import copy
import threading
from dataclasses import dataclass, field

from aiuthor.memory.schemas import (
    CallbackRecord,
    ConceptRecord,
    DecisionLogEntry,
    FactRecord,
    TonalitySurfaceRecord,
)


@dataclass
class BookMemoryState:
    """Mutable per-book state held in RAM."""

    book_id: str
    facts: list[FactRecord] = field(default_factory=list)
    concepts: list[ConceptRecord] = field(default_factory=list)
    callbacks: list[CallbackRecord] = field(default_factory=list)
    tonality: dict[str, TonalitySurfaceRecord] = field(default_factory=dict)
    decisions: list[DecisionLogEntry] = field(default_factory=list)


class InMemoryMemoryStore:
    """
    Thread-safe key/value of book_id -> BookMemoryState.

    Phase 2 default when AIUTHOR_MEMORY_BACKEND=memory. Data is lost on process restart.
    """

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._books: dict[str, BookMemoryState] = {}

    def get_or_create(self, book_id: str) -> BookMemoryState:
        with self._lock:
            if book_id not in self._books:
                self._books[book_id] = BookMemoryState(book_id=book_id)
            return self._books[book_id]

    def try_get(self, book_id: str) -> BookMemoryState | None:
        """Return state if the book exists; do not create a new shell book."""
        with self._lock:
            return self._books.get(book_id)

    def clone_snapshot(self, book_id: str) -> BookMemoryState | None:
        """Deep copy for API responses (avoid accidental mutation by callers)."""
        with self._lock:
            st = self._books.get(book_id)
            if st is None:
                return None
            return copy.deepcopy(st)

    def reset_book(self, book_id: str) -> None:
        with self._lock:
            self._books[book_id] = BookMemoryState(book_id=book_id)


_default_store: InMemoryMemoryStore | None = None
_store_lock = threading.Lock()


def get_memory_store() -> InMemoryMemoryStore:
    global _default_store
    with _store_lock:
        if _default_store is None:
            _default_store = InMemoryMemoryStore()
        return _default_store


def reset_memory_store_for_tests() -> None:
    """Test helper: clear singleton."""
    global _default_store
    with _store_lock:
        _default_store = InMemoryMemoryStore()
