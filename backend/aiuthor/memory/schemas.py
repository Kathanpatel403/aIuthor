"""Pydantic models for Redis/in-memory memory stores (Phase 2)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class FactRecord(BaseModel):
    """Atomic claim the Fact-Checker and citations can bind to."""

    id: str
    chapter_number: int = Field(..., ge=1)
    claim_text: str = Field(..., min_length=1)
    source_url: str | None = None
    evidence_snippet: str | None = None
    confidence: Literal["high", "medium", "low"] = "medium"
    created_at: datetime = Field(default_factory=utcnow)


class ConceptRecord(BaseModel):
    """Glossary / character or world-building entry."""

    id: str
    term: str = Field(..., min_length=1)
    definition: str = Field(..., min_length=1)
    first_mentioned_chapter: int = Field(..., ge=1)
    aliases: list[str] = Field(default_factory=list)
    kind: Literal["term", "character", "location", "other"] = "term"


class CallbackRecord(BaseModel):
    """Explicit cross-chapter link (echo, foreshadow, payoff)."""

    id: str
    from_chapter: int = Field(..., ge=1)
    to_chapter: int = Field(..., ge=1)
    kind: Literal["echo", "foreshadow", "payoff", "motif"] = "echo"
    snippet: str = Field(..., min_length=1)


class TonalitySurfaceRecord(BaseModel):
    """Fingerprint payload for a single textual surface (preface, glossary, …)."""

    surface: str = Field(..., min_length=1)
    embedding: list[float] | None = None
    exemplar_text: str | None = None
    updated_at: datetime = Field(default_factory=utcnow)


class DecisionLogEntry(BaseModel):
    """Append-only planner / memory-keeper decision."""

    id: str
    agent: str = Field(..., min_length=1)
    action: str = Field(..., min_length=1)
    details: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utcnow)


class ChapterInsertRepairReport(BaseModel):
    """Summary emitted after shifting chapter indices (Test D)."""

    book_id: str
    insert_after_chapter: int
    shifted_facts: int = 0
    shifted_concepts: int = 0
    shifted_callbacks: int = 0


class MemorySnapshot(BaseModel):
    """Full read model for GET /memory/{book_id}."""

    book_id: str
    facts: list[FactRecord]
    concepts: list[ConceptRecord]
    callbacks: list[CallbackRecord]
    tonality: dict[str, TonalitySurfaceRecord]
    decisions: list[DecisionLogEntry]
