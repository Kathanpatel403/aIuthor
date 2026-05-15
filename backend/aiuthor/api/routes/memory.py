"""Memory read + chapter-insert repair (Phase 2)."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from aiuthor.memory import (
    MemorySnapshot,
    get_memory_store,
    repair_after_chapter_insert,
)
from aiuthor.memory.schemas import ChapterInsertRepairReport

router = APIRouter()


def _snapshot_for_book(book_id: str) -> MemorySnapshot:
    store = get_memory_store()
    st = store.try_get(book_id)
    if st is None:
        return MemorySnapshot(
            book_id=book_id,
            facts=[],
            concepts=[],
            callbacks=[],
            tonality={},
            decisions=[],
        )
    clone = store.clone_snapshot(book_id)
    assert clone is not None
    return MemorySnapshot(
        book_id=clone.book_id,
        facts=list(clone.facts),
        concepts=list(clone.concepts),
        callbacks=list(clone.callbacks),
        tonality=dict(clone.tonality),
        decisions=list(clone.decisions),
    )


@router.get("/{book_id}", response_model=MemorySnapshot)
def read_memory(book_id: str) -> MemorySnapshot:
    """Return the full memory snapshot for a book (empty shell if never written)."""
    if not book_id.strip():
        raise HTTPException(status_code=400, detail="book_id required")
    return _snapshot_for_book(book_id.strip())


class ChapterInsertRepairBody(BaseModel):
    insert_after_chapter: int = Field(..., ge=0, description="New chapter is inserted after this index (0 = before ch.1)")


@router.post("/{book_id}/chapter-insert-repair", response_model=ChapterInsertRepairReport)
def chapter_insert_repair(book_id: str, body: ChapterInsertRepairBody) -> ChapterInsertRepairReport:
    """
    Run multi-store renumbering after inserting a chapter mid-outline (Assessment Test D).

    Semantics match `repair_after_chapter_insert`: every chapter index strictly greater than
    `insert_after_chapter` increments by one across facts, concepts, and callbacks.
    """
    bid = book_id.strip()
    if not bid:
        raise HTTPException(status_code=400, detail="book_id required")
    # Ensure shell book exists so clients can call repair without a prior write ordering.
    get_memory_store().get_or_create(bid)
    return repair_after_chapter_insert(bid, body.insert_after_chapter)
