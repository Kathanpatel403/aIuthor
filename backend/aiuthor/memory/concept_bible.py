"""Concept / character bible — glossary source of truth."""

from __future__ import annotations

import uuid
from typing import Literal

from aiuthor.memory.schemas import ConceptRecord
from aiuthor.memory.store import BookMemoryState, get_memory_store

ConceptKind = Literal["term", "character", "location", "other"]


class ConceptBible:
    def __init__(self, book_id: str) -> None:
        self._book_id = book_id
        self._store = get_memory_store()

    def _state(self) -> BookMemoryState:
        return self._store.get_or_create(self._book_id)

    def upsert(self, concept: ConceptRecord) -> ConceptRecord:
        st = self._state()
        with self._store._lock:
            for i, c in enumerate(st.concepts):
                if c.term.lower() == concept.term.lower():
                    st.concepts[i] = concept
                    return concept
            st.concepts.append(concept)
            return concept

    def add_concept(
        self,
        *,
        term: str,
        definition: str,
        first_mentioned_chapter: int,
        aliases: list[str] | None = None,
        kind: ConceptKind = "term",
    ) -> ConceptRecord:
        rec = ConceptRecord(
            id=str(uuid.uuid4()),
            term=term.strip(),
            definition=definition.strip(),
            first_mentioned_chapter=first_mentioned_chapter,
            aliases=list(aliases or []),
            kind=kind,
        )
        return self.upsert(rec)

    def list_all(self) -> list[ConceptRecord]:
        st = self._state()
        with self._store._lock:
            return list(st.concepts)

    def shift_chapters_after_insert(self, insert_after_chapter: int) -> int:
        st = self._state()
        count = 0
        with self._store._lock:
            for c in st.concepts:
                if c.first_mentioned_chapter > insert_after_chapter:
                    c.first_mentioned_chapter += 1
                    count += 1
        return count
