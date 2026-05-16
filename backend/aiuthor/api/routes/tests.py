"""Special endpoint to run the specific Audit Test Cases (A, B, C, D)."""

from __future__ import annotations
import uuid
import time
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from aiuthor.schemas.brief import UserBrief
from aiuthor.orchestrator.dag import run_book_pipeline
from aiuthor.api.pipeline_jobs import job_create, job_get
from aiuthor.api.routes.tone_variants import _generate_variant
from aiuthor.api.routes.chapter_insert import ChapterInsertRequest, insert_chapter

router = APIRouter()

# Global to keep track of the "Test A" book_id so C and D can use it
TEST_A_BOOK_ID = None

class TestStatus(BaseModel):
    test_id: str
    book_id: str | None = None
    status: str
    download_urls: dict[str, str] | None = None

@router.post("/run/{test_id}")
async def run_audit_test(test_id: str, background_tasks: BackgroundTasks):
    global TEST_A_BOOK_ID
    
    if test_id == "test_a":
        # Test A: Personal Finance, 10 chapters, Conversational, ~2500 words
        brief = {
            "topic": "The Wealth Blueprint: A Modern Guide to Personal Finance",
            "reader_profile": "Young professionals looking to master budgeting and investing",
            "genre": "nonfiction",
            "tonality": "conversational",
            "chapter_count": 10,
            "words_per_chapter": 2500
        }
        book_id = str(uuid.uuid4())
        TEST_A_BOOK_ID = book_id # Save for C and D
        job_create(book_id, brief)
        background_tasks.add_task(run_book_pipeline, book_id, brief)
        return {"book_id": book_id, "message": "Test A started"}

    elif test_id == "test_b":
        # Test B: 5-chapter novella, Storyteller tone, two named characters
        brief = {
            "topic": "The Clockmaker's Secret: A tale of Elias and Clara in old Prague",
            "reader_profile": "Lovers of historical fiction and mystery",
            "genre": "novella",
            "tonality": "storyteller",
            "chapter_count": 5,
            "words_per_chapter": 2000,
            "constraints": "Must feature characters Elias and Clara throughout."
        }
        book_id = str(uuid.uuid4())
        job_create(book_id, brief)
        background_tasks.add_task(run_book_pipeline, book_id, brief)
        return {"book_id": book_id, "message": "Test B started"}

    elif test_id == "test_c":
        if not TEST_A_BOOK_ID:
            raise HTTPException(status_code=400, detail="Test A must be run first to provide a source for Test C")
        
        # Test C: Regenerate Test A's Chapter 3 in Academic, Motivational, Witty
        # This is a synchronous 'mini-task' for the background
        def run_c():
            for tone in ["academic", "motivational", "witty"]:
                _generate_variant(TEST_A_BOOK_ID, 3, tone)
        
        background_tasks.add_task(run_c)
        return {"book_id": TEST_A_BOOK_ID, "message": "Test C variants started for Chapter 3"}

    elif test_id == "test_d":
        if not TEST_A_BOOK_ID:
            raise HTTPException(status_code=400, detail="Test A must be run first to provide a source for Test D")
        
        # Test D: Insert chapter between Ch 4 and Ch 5 of Test A
        req = ChapterInsertRequest(
            after_chapter=4,
            title="The Psychology of Spending: Why We Buy What We Don't Need",
            summary="An exploration of behavioral economics and the emotional triggers of consumerism.",
            key_points=["The dopamine loop", "Social signaling", "Mindful spending habits"]
        )
        background_tasks.add_task(insert_chapter, TEST_A_BOOK_ID, req)
        return {"book_id": TEST_A_BOOK_ID, "message": "Test D insertion started"}

    else:
        raise HTTPException(status_code=404, detail="Unknown test ID")
