"""Run full book pipeline (Phase 5) + async job start for UI (Phase 8)."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel

from aiuthor.api.pipeline_jobs import job_create, job_get
from aiuthor.config.settings import get_settings
from aiuthor.orchestrator.dag import run_book_pipeline
from aiuthor.schemas.brief import UserBrief

router = APIRouter()


class PipelineResponse(BaseModel):
    book_id: str
    export_paths: dict[str, str]
    trace_bundle_paths: dict[str, str]


class PipelineStartResponse(BaseModel):
    book_id: str


class PipelineStatusResponse(BaseModel):
    book_id: str
    status: str
    stage: str | None
    chapter_index: int | None
    total_chapters: int | None
    current_agent: str | None
    error: str | None
    export_paths: dict[str, str] | None
    trace_bundle_paths: dict[str, str] | None
    brief_summary: dict | None


def _require_pipeline_keys(settings) -> None:
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=400,
            detail="OPENAI_API_KEY is required to run the agent pipeline (chat + embeddings)",
        )


def _brief_summary(brief: UserBrief) -> dict:
    return {
        "topic": brief.topic,
        "genre": brief.genre,
        "tonality": brief.tonality,
        "chapter_count": brief.chapter_count,
        "words_per_chapter": brief.words_per_chapter,
    }


def _run_pipeline_background(book_id: str, brief_dict: dict) -> None:
    """Background worker; status + completion are recorded via pipeline_jobs / dag."""
    run_book_pipeline(book_id, brief_dict)


@router.post("/pipeline/run", response_model=PipelineResponse)
def run_pipeline(brief: UserBrief) -> PipelineResponse:
    settings = get_settings()
    _require_pipeline_keys(settings)
    book_id = str(uuid.uuid4())
    result = run_book_pipeline(book_id, brief.model_dump())
    paths = result.get("export_paths") or {}
    if not paths:
        raise HTTPException(status_code=500, detail="Pipeline finished but no export paths were produced")
    bundle = result.get("trace_bundle_paths") or {}
    return PipelineResponse(book_id=book_id, export_paths=paths, trace_bundle_paths=bundle)


@router.post("/pipeline/start", response_model=PipelineStartResponse)
def start_pipeline(
    brief: UserBrief,
    background_tasks: BackgroundTasks,
) -> PipelineStartResponse:
    """Queue a full pipeline run and return immediately with book_id for status polling."""
    settings = get_settings()
    _require_pipeline_keys(settings)
    book_id = str(uuid.uuid4())
    job_create(book_id, _brief_summary(brief))
    background_tasks.add_task(_run_pipeline_background, book_id, brief.model_dump())
    return PipelineStartResponse(book_id=book_id)


@router.get("/pipeline/status/{book_id}", response_model=PipelineStatusResponse)
def pipeline_status(book_id: str) -> PipelineStatusResponse:
    bid = book_id.strip()
    if not bid:
        raise HTTPException(status_code=400, detail="book_id required")
    row = job_get(bid)
    if row is None:
        raise HTTPException(status_code=404, detail="No pipeline job found for this book_id (jobs are in-memory only)")
    return PipelineStatusResponse(
        book_id=row["book_id"],
        status=row["status"],
        stage=row.get("stage"),
        chapter_index=row.get("chapter_index"),
        total_chapters=row.get("total_chapters"),
        current_agent=row.get("current_agent"),
        error=row.get("error"),
        export_paths=row.get("export_paths"),
        trace_bundle_paths=row.get("trace_bundle_paths"),
        brief_summary=row.get("brief_summary"),
    )
