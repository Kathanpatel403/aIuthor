"""Fact registry: grounded claims indexed by chapter."""

from __future__ import annotations

import uuid
from typing import Literal

from aiuthor.memory.schemas import FactRecord
from aiuthor.memory.store import BookMemoryState, get_memory_store
from aiuthor.observability.memory_audit import log_memory_io


class FactRegistry:
    """Read/write facts for one book."""

    def __init__(self, book_id: str) -> None:
        self._book_id = book_id
        self._store = get_memory_store()

    def _state(self) -> BookMemoryState:
        return self._store.get_or_create(self._book_id)

    def append(self, fact: FactRecord) -> None:
        st = self._state()
        with self._store._lock:
            st.facts.append(fact)
        log_memory_io("write", "fact_registry", f"append claim={fact.claim_text[:120]!r}")
        self._store.touch_persist(self._book_id)

    def add_fact(
        self,
        *,
        chapter_number: int,
        claim_text: str,
        source_url: str | None = None,
        evidence_snippet: str | None = None,
        confidence: Literal["high", "medium", "low"] = "medium",
    ) -> FactRecord:
        rec = FactRecord(
            id=str(uuid.uuid4()),
            chapter_number=chapter_number,
            claim_text=claim_text,
            source_url=source_url,
            evidence_snippet=evidence_snippet,
            confidence=confidence,
        )
        self.append(rec)
        return rec

    def list_all(self) -> list[FactRecord]:
        st = self._state()
        with self._store._lock:
            n = len(st.facts)
            rows = list(st.facts)
        log_memory_io("read", "fact_registry", f"list_all count={n}")
        return rows

    def list_for_chapter(self, chapter_number: int) -> list[FactRecord]:
        return [f for f in self.list_all() if f.chapter_number == chapter_number]

    def shift_chapters_after_insert(self, insert_after_chapter: int) -> int:
        """
        New chapter inserted immediately after `insert_after_chapter`.
        Any existing chapter number > insert_after_chapter increments by 1.
        """
        st = self._state()
        count = 0
        with self._store._lock:
            for f in st.facts:
                if f.chapter_number > insert_after_chapter:
                    f.chapter_number += 1
                    count += 1
        if count:
            self._store.touch_persist(self._book_id)
        return count
