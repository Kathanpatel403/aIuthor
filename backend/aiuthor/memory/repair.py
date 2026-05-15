"""Coordinate multi-store repair when a chapter is inserted mid-book (Assessment Test D)."""

from __future__ import annotations

from aiuthor.memory.callback_index import CallbackIndex
from aiuthor.memory.concept_bible import ConceptBible
from aiuthor.memory.fact_registry import FactRegistry
from aiuthor.memory.schemas import ChapterInsertRepairReport


def repair_after_chapter_insert(book_id: str, insert_after_chapter: int) -> ChapterInsertRepairReport:
    """
    Insert semantics: a new body chapter is placed *after* `insert_after_chapter`.
    Existing chapters with index > insert_after_chapter shift up by 1 across all stores.
    """
    facts = FactRegistry(book_id).shift_chapters_after_insert(insert_after_chapter)
    concepts = ConceptBible(book_id).shift_chapters_after_insert(insert_after_chapter)
    callbacks = CallbackIndex(book_id).trigger_repair_after_chapter_insert(insert_after_chapter)
    return ChapterInsertRepairReport(
        book_id=book_id,
        insert_after_chapter=insert_after_chapter,
        shifted_facts=facts,
        shifted_concepts=concepts,
        shifted_callbacks=callbacks,
    )
