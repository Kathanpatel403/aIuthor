"""Base Pydantic contracts for user input and planner output (Phase 1)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator

TonalityPreset = Literal[
    "conversational",
    "academic",
    "storyteller",
    "motivational",
    "witty",
]


class UserBrief(BaseModel):
    """Input: what the reader asked for."""

    topic: str = Field(..., min_length=3, description="Core subject of the book")
    reader_profile: str = Field(
        ...,
        min_length=3,
        description="Who the book is for (experience level, goals, context)",
    )
    genre: str = Field(..., min_length=2, description="e.g. nonfiction, novella, how-to")
    tonality: TonalityPreset = Field(
        default="conversational",
        description="Voice preset; cascades to all surfaces in later phases",
    )
    chapter_count: int = Field(..., ge=1, le=50, description="Number of body chapters")
    words_per_chapter: int = Field(
        ...,
        ge=200,
        le=15000,
        description="Target words per chapter (assembly uses this for pacing notes)",
    )
    constraints: str | None = Field(
        default=None,
        description="Optional hard constraints (no medical advice, region-specific law, etc.)",
    )

    @field_validator("topic", "reader_profile", "genre", mode="before")
    @classmethod
    def strip_strings(cls, v: object) -> object:
        if isinstance(v, str):
            return v.strip()
        return v


class ChapterOutline(BaseModel):
    """Single chapter row inside a book outline."""

    number: int = Field(..., ge=1, description="1-based chapter index")
    title: str = Field(..., min_length=1)
    summary: str = Field(
        ...,
        min_length=10,
        description="What this chapter covers; feeds Researcher queries",
    )
    key_points: list[str] = Field(
        default_factory=list,
        description="Bullet targets for Writer; Memory Keeper may index these",
    )


class BookOutline(BaseModel):
    """Output shape for Planner agent (Phase 5)."""

    title: str = Field(..., min_length=1)
    subtitle: str | None = None
    logline: str = Field(..., min_length=10, description="One-paragraph pitch")
    audience: str = Field(..., min_length=3)
    genre: str = Field(..., min_length=2)
    default_tonality: TonalityPreset = "conversational"
    themes: list[str] = Field(default_factory=list, max_length=20)
    chapters: list[ChapterOutline] = Field(..., min_length=1)

    @field_validator("chapters")
    @classmethod
    def chapters_sorted_and_sequential(cls, chapters: list[ChapterOutline]) -> list[ChapterOutline]:
        nums = [c.number for c in chapters]
        if sorted(nums) != list(range(1, len(chapters) + 1)):
            raise ValueError("chapters must be numbered 1..N with no gaps or duplicates")
        return sorted(chapters, key=lambda c: c.number)
