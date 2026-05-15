"""Trigger automated evaluation for a generated book."""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from aiuthor.evals.runner import run_eval_suite
from aiuthor.evals.schemas import EvalReport

router = APIRouter()


class EvalRequest(BaseModel):
    markdown_override: str | None = Field(default=None, description="Optional full Markdown instead of sample_books file")


TonalityQuery = Literal["conversational", "academic", "storyteller", "motivational", "witty"]


@router.post("/{book_id}", response_model=EvalReport)
def run_evals(
    book_id: str,
    target_tonality: TonalityQuery = "conversational",
    body: EvalRequest | None = None,
) -> EvalReport:
    bid = book_id.strip()
    if not bid:
        raise HTTPException(status_code=400, detail="book_id required")
    try:
        return run_eval_suite(
            bid,
            target_tonality=target_tonality,
            markdown_override=(body.markdown_override if body else None),
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"book.md not found under sample_books/{bid}/ — generate the book first or pass markdown_override",
        ) from None
