"""Test D — Insert a new chapter at a given position with full self-healing.

POST /api/v1/books/{book_id}/chapters/insert
Body: {
  "after_chapter": 4,
  "title": "The Psychology of Spending",
  "summary": "...",
  "key_points": ["..."]
}

Self-healing:
  1. Memory stores: shift fact/concept/callback chapter numbers > after_chapter by +1
  2. Chapter bodies list: insert new body at position after_chapter (0-indexed)
  3. BookOutline: renumber chapters > after_chapter by +1, insert new ChapterOutline
  4. Re-run assembler: rebuild book.html + PDF + DOCX
  5. Persist updated outline.json + chapters.json
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from aiuthor.agents.editor import run_editor
from aiuthor.agents.humanizer import run_humanizer
from aiuthor.agents.memory_keeper import run_memory_keeper
from aiuthor.agents.researcher import run_researcher
from aiuthor.agents.writer import run_writer
from aiuthor.assembler.book_state import load_chapters, load_outline, save_book_state
from aiuthor.assembler.pipeline import assemble_book
from aiuthor.config.settings import get_settings
from aiuthor.memory.repair import repair_after_chapter_insert
from aiuthor.memory.schemas import ChapterInsertRepairReport
from aiuthor.schemas.brief import BookOutline, ChapterOutline

router = APIRouter()


class ChapterInsertRequest(BaseModel):
    after_chapter: int = Field(..., ge=1, description="Insert the new chapter AFTER this chapter number")
    title: str = Field(..., min_length=1, description="Title of the new chapter")
    summary: str = Field(..., min_length=10, description="What this chapter covers")
    key_points: list[str] = Field(default_factory=list)


class ChapterInsertResponse(BaseModel):
    book_id: str
    inserted_chapter_number: int
    new_total_chapters: int
    repair_report: ChapterInsertRepairReport
    export_paths: dict[str, str]


def _rebuild_outline(
    outline: BookOutline,
    after_chapter: int,
    new_ch: ChapterOutline,
) -> BookOutline:
    """Return a new BookOutline with the chapter inserted and existing chapters renumbered."""
    new_chapters: list[ChapterOutline] = []
    for ch in outline.chapters:
        if ch.number <= after_chapter:
            new_chapters.append(ch)
        else:
            # Renumber upward
            new_chapters.append(
                ChapterOutline(
                    number=ch.number + 1,
                    title=ch.title,
                    summary=ch.summary,
                    key_points=ch.key_points,
                )
            )
    new_chapters.append(new_ch)
    # Sort to correct order
    new_chapters.sort(key=lambda c: c.number)

    return BookOutline(
        title=outline.title,
        subtitle=outline.subtitle,
        logline=outline.logline,
        audience=outline.audience,
        genre=outline.genre,
        default_tonality=outline.default_tonality,
        themes=outline.themes,
        chapters=new_chapters,
    )


@router.post("/{book_id}/chapters/insert", response_model=ChapterInsertResponse)
def insert_chapter(book_id: str, body: ChapterInsertRequest) -> ChapterInsertResponse:
    """Test D — Insert a chapter mid-book with self-healing TOC/callbacks/glossary."""
    bid = book_id.strip()
    if not bid:
        raise HTTPException(status_code=400, detail="book_id required")

    settings = get_settings()
    if not settings.openai_api_key:
        raise HTTPException(status_code=400, detail="OPENAI_API_KEY required")

    # Load existing book state
    try:
        outline = load_outline(bid)
        chapter_bodies = load_chapters(bid)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    after = body.after_chapter
    if after < 1 or after >= len(outline.chapters) + 1:
        raise HTTPException(
            status_code=422,
            detail=f"after_chapter={after} is out of range (book has {len(outline.chapters)} chapters)",
        )

    # --- Step 1: Self-heal memory stores (shift chapter indices) ---
    repair_report = repair_after_chapter_insert(bid, after)

    # --- Step 2: Assign the new chapter number ---
    new_number = after + 1
    new_ch_outline = ChapterOutline(
        number=new_number,
        title=body.title,
        summary=body.summary,
        key_points=body.key_points,
    )

    # --- Step 3: Generate the new chapter (researcher → writer → humanizer → editor → memory) ---
    fact_pack = run_researcher(bid, new_ch_outline, settings)

    raw = run_writer(
        outline.title,
        outline.genre,
        new_ch_outline,
        fact_pack,
        str(outline.default_tonality),
        target_words=2500,
        settings=settings,
        book_id=bid,
    )

    humanized = run_humanizer(raw, str(outline.default_tonality), settings)

    edited = run_editor(bid, new_number, humanized, str(outline.default_tonality), settings)

    run_memory_keeper(bid, new_number, edited, str(outline.default_tonality), settings)

    # --- Step 4: Rebuild outline and chapter bodies ---
    new_outline = _rebuild_outline(outline, after, new_ch_outline)

    # Insert the new body at the correct 0-based position (after_chapter is 1-based)
    new_bodies = list(chapter_bodies)
    new_bodies.insert(after, edited)  # index `after` == position after chapter `after`

    # --- Step 5: Re-assemble the book ---
    try:
        _, paths = assemble_book(bid, new_outline, new_bodies, settings)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Assembler failed: {exc}") from exc

    return ChapterInsertResponse(
        book_id=bid,
        inserted_chapter_number=new_number,
        new_total_chapters=len(new_outline.chapters),
        repair_report=repair_report,
        export_paths=paths,
    )
