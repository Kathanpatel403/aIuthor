"""Evaluation report schema (Phase 7)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class DimensionScore(BaseModel):
    name: str
    score: float = Field(..., ge=0.0, le=1.0)
    weight: float = Field(..., ge=0.0, le=1.0)
    detail: str = ""


class EvalReport(BaseModel):
    book_id: str
    markdown_source: str
    overall_score: float = Field(..., ge=0.0, le=1.0)
    dimensions: list[DimensionScore]
    failure_analysis: list[str] = Field(default_factory=list)
    rubric_version: str = "aiuthor-eval-v1"
