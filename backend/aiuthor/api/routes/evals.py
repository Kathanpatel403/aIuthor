"""Trigger automated evaluation for a generated book."""

from __future__ import annotations

import json
from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from aiuthor.evals.runner import run_eval_suite
from aiuthor.evals.schemas import EvalReport
from aiuthor.paths import traces_dir

router = APIRouter()


class EvalRequest(BaseModel):
    markdown_override: str | None = Field(default=None, description="Optional full Markdown instead of sample_books file")


TonalityQuery = Literal["conversational", "academic", "storyteller", "motivational", "witty"]


@router.get("/{book_id}/report", response_model=EvalReport)
def get_eval_report(book_id: str) -> EvalReport:
    """Return the last persisted eval report from traces/{book_id}/evals_report.json."""
    bid = book_id.strip()
    if not bid:
        raise HTTPException(status_code=400, detail="book_id required")
    path = traces_dir(bid) / "evals_report.json"
    if not path.is_file():
        raise HTTPException(
            status_code=404,
            detail="No eval report on disk yet — run POST /evals/{book_id} first",
        )
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return EvalReport.model_validate(data)
    except (json.JSONDecodeError, ValueError) as exc:
        raise HTTPException(status_code=500, detail=f"Invalid eval report file: {exc}") from exc


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
            detail=f"book.html not found under sample_books/{bid}/ — generate the book first or pass markdown_override",
        ) from None
