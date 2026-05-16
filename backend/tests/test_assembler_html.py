"""HTML book assembly and export smoke tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from aiuthor.assembler.book_io import parse_chapters_from_html
from aiuthor.assembler.html_builder import render_book_html
from aiuthor.assembler.pdf_builder import html_to_pdf
from aiuthor.schemas.brief import BookOutline, ChapterOutline


def _mini_outline() -> BookOutline:
    return BookOutline(
        title="Test Book",
        logline="A short test book for export smoke tests.",
        audience="Developers",
        genre="Technical",
        chapters=[
            ChapterOutline(number=1, title="Alpha", summary="First chapter summary."),
            ChapterOutline(number=2, title="Beta", summary="Second chapter summary."),
        ],
    )


def test_render_book_html_has_chapters_and_sections():
    html = render_book_html(
        "test-book",
        _mini_outline(),
        ["Body one.", "Body two with **bold**."],
    )
    assert "<!DOCTYPE html>" in html
    assert 'id="chapter-1"' in html
    assert 'id="chapter-2"' in html
    assert 'id="contents"' in html
    assert "Alpha" in html
    chapters = parse_chapters_from_html(html)
    assert len(chapters) == 2
    assert chapters[0]["title"] == "Alpha"
    assert "Body one" in chapters[0]["body"]


def test_html_to_pdf_writes_file(tmp_path: Path):
    html = render_book_html("pdf-test", _mini_outline(), ["Chapter one.", "Chapter two."])
    out = tmp_path / "book.pdf"
    try:
        html_to_pdf(html, out)
    except RuntimeError as exc:
        pytest.skip(f"PDF engine not available: {exc}")
    assert out.is_file()
    assert out.stat().st_size > 500
