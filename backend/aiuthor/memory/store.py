"""Process-local in-memory book store (Redis-swappable interface)."""

from __future__ import annotations

import copy
import json
import logging
import os
import re
import threading
from dataclasses import dataclass, field
from pathlib import Path

from aiuthor.memory.schemas import (
    CallbackRecord,
    ConceptRecord,
    DecisionLogEntry,
    FactRecord,
    TonalitySurfaceRecord,
)

logger = logging.getLogger(__name__)


@dataclass
class BookMemoryState:
    """Mutable per-book state held in RAM."""

    book_id: str
    facts: list[FactRecord] = field(default_factory=list)
    concepts: list[ConceptRecord] = field(default_factory=list)
    callbacks: list[CallbackRecord] = field(default_factory=list)
    tonality: dict[str, TonalitySurfaceRecord] = field(default_factory=dict)
    decisions: list[DecisionLogEntry] = field(default_factory=list)


def _sanitize_book_id_fs(book_id: str) -> str:
    safe = re.sub(r"[^\w\-]+", "_", book_id.strip())
    return (safe[:200] if safe else "unknown") or "unknown"


def _persist_root() -> Path:
    from aiuthor.config.settings import get_settings
    from aiuthor.paths import memory_data_dir

    override = get_settings().aiuthor_memory_data_dir
    if override:
        p = Path(override).expanduser()
        p.mkdir(parents=True, exist_ok=True)
        return p
    return memory_data_dir()


def _persist_path(book_id: str) -> Path:
    return _persist_root() / f"{_sanitize_book_id_fs(book_id)}.json"


def _persist_enabled() -> bool:
    from aiuthor.config.settings import get_settings

    if get_settings().aiuthor_memory_backend != "memory":
        return False
    return bool(get_settings().aiuthor_memory_persist)


def _serialize_state(st: BookMemoryState) -> dict:
    return {
        "book_id": st.book_id,
        "facts": [f.model_dump(mode="json") for f in st.facts],
        "concepts": [c.model_dump(mode="json") for c in st.concepts],
        "callbacks": [c.model_dump(mode="json") for c in st.callbacks],
        "tonality": {k: v.model_dump(mode="json") for k, v in st.tonality.items()},
        "decisions": [d.model_dump(mode="json") for d in st.decisions],
    }


def _deserialize_state(data: dict, book_id: str) -> BookMemoryState | None:
    try:
        bid = str(data.get("book_id") or book_id)
        facts = [FactRecord.model_validate(x) for x in data.get("facts") or []]
        concepts = [ConceptRecord.model_validate(x) for x in data.get("concepts") or []]
        callbacks = [CallbackRecord.model_validate(x) for x in data.get("callbacks") or []]
        tonality = {
            k: TonalitySurfaceRecord.model_validate(v) for k, v in (data.get("tonality") or {}).items()
        }
        decisions = [DecisionLogEntry.model_validate(x) for x in data.get("decisions") or []]
        return BookMemoryState(
            book_id=bid,
            facts=facts,
            concepts=concepts,
            callbacks=callbacks,
            tonality=tonality,
            decisions=decisions,
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("memory snapshot JSON invalid for book_id=%s: %s", book_id, exc)
        return None


class InMemoryMemoryStore:
    """
    Thread-safe key/value of book_id -> BookMemoryState.

    Phase 2 default when AIUTHOR_MEMORY_BACKEND=memory. With AIUTHOR_MEMORY_PERSIST=true
    (default), each book is snapshotted to JSON under memory_data/ so restarts keep facts,
    concepts, callbacks, etc. (Run repair then has stable chapter indices to shift.)
    """

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._books: dict[str, BookMemoryState] = {}

    def get_or_create(self, book_id: str) -> BookMemoryState:
        with self._lock:
            if book_id not in self._books:
                shell = BookMemoryState(book_id=book_id)
                if _persist_enabled():
                    loaded = self._try_load(book_id)
                    self._books[book_id] = loaded if loaded is not None else shell
                else:
                    self._books[book_id] = shell
            return self._books[book_id]

    def _try_load(self, book_id: str) -> BookMemoryState | None:
        path = _persist_path(book_id)
        if not path.is_file():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                return None
            return _deserialize_state(data, book_id)
        except OSError as exc:
            logger.warning("memory snapshot read failed book_id=%s path=%s: %s", book_id, path, exc)
            return None
        except json.JSONDecodeError as exc:
            logger.warning("memory snapshot JSON decode failed book_id=%s path=%s: %s", book_id, path, exc)
            return None

    def touch_persist(self, book_id: str) -> None:
        """Write current in-RAM book state to disk (no-op if persistence disabled)."""
        if not _persist_enabled():
            return
        with self._lock:
            st = self._books.get(book_id)
            if st is None:
                return
            payload = _serialize_state(st)
        path = _persist_path(book_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        body = json.dumps(payload, ensure_ascii=False, indent=2)
        tmp.write_text(body, encoding="utf-8")
        os.replace(tmp, path)

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
        if _persist_enabled():
            path = _persist_path(book_id)
            try:
                if path.is_file():
                    path.unlink()
            except OSError as exc:
                logger.warning("could not remove memory snapshot %s: %s", path, exc)


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
