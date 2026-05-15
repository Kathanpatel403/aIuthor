"""Run full book pipeline (Phase 5)."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from aiuthor.config.settings import get_settings
from aiuthor.orchestrator.dag import run_book_pipeline
from aiuthor.schemas.brief import UserBrief

router = APIRouter()


class PipelineResponse(BaseModel):
    book_id: str
    export_paths: dict[str, str]
    trace_bundle_paths: dict[str, str]


@router.post("/pipeline/run", response_model=PipelineResponse)
def run_pipeline(brief: UserBrief) -> PipelineResponse:
    settings = get_settings()
    if not settings.anthropic_api_key:
        raise HTTPException(status_code=400, detail="ANTHROPIC_API_KEY is required to run the agent pipeline")
    if not settings.openai_api_key:
        raise HTTPException(status_code=400, detail="OPENAI_API_KEY is required for embeddings (RAG + fingerprints)")
    book_id = str(uuid.uuid4())
    result = run_book_pipeline(book_id, brief.model_dump())
    paths = result.get("export_paths") or {}
    if not paths:
        raise HTTPException(status_code=500, detail="Pipeline finished but no export paths were produced")
    bundle = result.get("trace_bundle_paths") or {}
    return PipelineResponse(book_id=book_id, export_paths=paths, trace_bundle_paths=bundle)
