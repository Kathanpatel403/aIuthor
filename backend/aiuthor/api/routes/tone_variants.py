"""Test C — Re-generate a single chapter in one or more alternate tonalities.

POST /api/v1/books/{book_id}/chapters/{chapter_number}/tone-variants
Body: { "tones": ["academic", "motivational", "witty"] }

Returns: { "variants": { "academic": "...", "motivational": "...", "witty": "..." } }

The original chapter is NOT overwritten. Variants are saved as
sample_books/{book_id}/chapter_{N}_{tone}.md
"""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel

from aiuthor.assembler.book_state import load_chapters, load_outline
from aiuthor.agents.humanizer import run_humanizer
from aiuthor.agents.researcher import run_researcher
from aiuthor.agents.writer import run_writer
from aiuthor.config.settings import get_settings
from aiuthor.paths import sample_books_dir
from aiuthor.schemas.brief import TonalityPreset

router = APIRouter()

_VALID_TONES: set[str] = {"conversational", "academic", "storyteller", "motivational", "witty"}


class ToneVariantRequest(BaseModel):
    tones: list[TonalityPreset]


class ToneVariantResponse(BaseModel):
    book_id: str
    chapter_number: int
    original_tone: str
    variants: dict[str, str]


def _variant_path(book_id: str, chapter_number: int, tone: str) -> Path:
    return sample_books_dir() / book_id / f"chapter_{chapter_number}_{tone}.md"


def _generate_variant(
    book_id: str,
    chapter_number: int,
    tone: str,
) -> str:
    """Run researcher→writer→humanizer for one tone variant of one chapter."""
    settings = get_settings()
    outline = load_outline(book_id)

    # Find the chapter outline
    ch = next((c for c in outline.chapters if c.number == chapter_number), None)
    if ch is None:
        raise ValueError(f"Chapter {chapter_number} not found in outline for book {book_id}")

    # Researcher (re-use existing RAG data if available — same namespace as original)
    fact_pack = run_researcher(book_id, ch, settings)

    # Writer with alternate tone
    raw = run_writer(
        outline.title,
        outline.genre,
        ch,
        fact_pack,
        tone,
        target_words=2500,          # sensible default for variants
        settings=settings,
        book_id=book_id,
    )

    # Humanizer
    humanized = run_humanizer(raw, tone, settings)

    # Persist variant to disk
    out = _variant_path(book_id, chapter_number, tone)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(humanized, encoding="utf-8")

    return humanized


@router.post("/{book_id}/chapters/{chapter_number}/tone-variants", response_model=ToneVariantResponse)
def generate_tone_variants(
    book_id: str,
    chapter_number: int,
    body: ToneVariantRequest,
) -> ToneVariantResponse:
    """Test C — regenerate chapter N in requested tone(s) without touching the original book."""
    bid = book_id.strip()
    if not bid:
        raise HTTPException(status_code=400, detail="book_id required")
    if chapter_number < 1:
        raise HTTPException(status_code=400, detail="chapter_number must be >= 1")
    if not body.tones:
        raise HTTPException(status_code=400, detail="at least one tone required")
    invalid = [t for t in body.tones if t not in _VALID_TONES]
    if invalid:
        raise HTTPException(
            status_code=422,
            detail=f"Unknown tone(s): {invalid}. Valid: {sorted(_VALID_TONES)}",
        )

    try:
        outline = load_outline(bid)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    ch = next((c for c in outline.chapters if c.number == chapter_number), None)
    if ch is None:
        raise HTTPException(
            status_code=404,
            detail=f"Chapter {chapter_number} not found (book has {len(outline.chapters)} chapters)",
        )

    settings = get_settings()
    if not settings.openai_api_key:
        raise HTTPException(status_code=400, detail="OPENAI_API_KEY required to generate variants")

    variants: dict[str, str] = {}
    for tone in body.tones:
        try:
            variants[tone] = _generate_variant(bid, chapter_number, tone)
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(
                status_code=500, detail=f"Failed generating variant for tone={tone}: {exc}"
            ) from exc

    return ToneVariantResponse(
        book_id=bid,
        chapter_number=chapter_number,
        original_tone=str(outline.default_tonality),
        variants=variants,
    )
