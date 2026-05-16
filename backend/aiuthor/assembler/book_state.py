"""Persist and reload BookOutline + chapter bodies to/from disk.

This is the missing link that enables Test C (tone variants) and Test D (chapter insert):
both require reloading a previously generated book without re-running the full pipeline.

Files written per book_id under sample_books/{book_id}/:
  outline.json   — serialised BookOutline
  chapters.json  — list[str] of final chapter markdown bodies (indexed 0..N-1)
"""

from __future__ import annotations

import json
from pathlib import Path

from aiuthor.paths import sample_books_dir
from aiuthor.schemas.brief import BookOutline


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------


def _book_dir(book_id: str) -> Path:
    return sample_books_dir() / book_id.strip()


def outline_path(book_id: str) -> Path:
    return _book_dir(book_id) / "outline.json"


def chapters_path(book_id: str) -> Path:
    return _book_dir(book_id) / "chapters.json"


# ---------------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------------


def save_book_state(book_id: str, outline: BookOutline, chapter_bodies: list[str]) -> None:
    """Persist outline + bodies immediately after assembly."""
    d = _book_dir(book_id)
    d.mkdir(parents=True, exist_ok=True)
    outline_path(book_id).write_text(outline.model_dump_json(indent=2), encoding="utf-8")
    chapters_path(book_id).write_text(json.dumps(chapter_bodies, ensure_ascii=False, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# Load
# ---------------------------------------------------------------------------


def load_outline(book_id: str) -> BookOutline:
    p = outline_path(book_id)
    if not p.is_file():
        raise FileNotFoundError(
            f"outline.json not found for book_id={book_id!r}. "
            "Run the full pipeline at least once first."
        )
    return BookOutline.model_validate_json(p.read_text(encoding="utf-8"))


def load_chapters(book_id: str) -> list[str]:
    p = chapters_path(book_id)
    if not p.is_file():
        raise FileNotFoundError(
            f"chapters.json not found for book_id={book_id!r}. "
            "Run the full pipeline at least once first."
        )
    return json.loads(p.read_text(encoding="utf-8"))


def book_state_exists(book_id: str) -> bool:
    return outline_path(book_id).is_file() and chapters_path(book_id).is_file()
