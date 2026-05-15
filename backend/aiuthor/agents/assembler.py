"""Assembler agent — file outputs."""

from __future__ import annotations

from aiuthor.assembler.pipeline import assemble_book
from aiuthor.config.settings import Settings
from aiuthor.schemas.brief import BookOutline


def run_assembler(book_id: str, outline: BookOutline, chapter_bodies: list[str], settings: Settings) -> dict[str, str]:
    _, paths = assemble_book(book_id, outline, chapter_bodies, settings)
    return paths
