"""Typed handoffs between agents (documentation + validation helpers)."""

from __future__ import annotations

from pydantic import BaseModel, Field

from aiuthor.rag.schemas import ChapterFactPack


class ResearcherOutput(BaseModel):
    chapter_number: int
    fact_pack: ChapterFactPack


class WriterInput(BaseModel):
    chapter_number: int
    chapter_title: str
    chapter_summary: str
    target_words: int
    tonality: str
    fact_pack: ChapterFactPack
    outline_title: str
    genre: str


class ChapterArtifact(BaseModel):
    chapter_number: int
    title: str
    raw_draft: str = ""
    humanized: str = ""
    edited: str = ""
    fact_checked: str = ""


class AssemblerInput(BaseModel):
    book_id: str
    tonality: str
    outline_title: str
    audience: str
    genre: str
    chapters: list[tuple[int, str, str]] = Field(
        default_factory=list,
        description="(number, title, markdown_body)",
    )
    concepts: list[tuple[str, str]] = Field(default_factory=list, description="(term, definition)")
