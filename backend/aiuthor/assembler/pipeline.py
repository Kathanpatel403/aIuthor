"""Glue front matter, body, back matter; write HTML source + PDF + DOCX."""

from __future__ import annotations

from aiuthor.assembler.book_state import save_book_state
from aiuthor.assembler.docx_builder import html_to_docx
from aiuthor.assembler.html_builder import render_book_html
from aiuthor.assembler.pdf_builder import html_to_pdf
from aiuthor.config.settings import Settings
from aiuthor.paths import sample_books_dir
from aiuthor.schemas.brief import BookOutline


def assemble_book(
    book_id: str,
    outline: BookOutline,
    chapter_bodies: list[str],
    settings: Settings,
) -> tuple[str, dict[str, str]]:
    """
    Returns (html, paths with html/pdf/docx).

    book.html is the canonical source for exports and preview.
    outline.json + chapters.json are written for Test C / D reload.
    """
    _ = settings
    html = render_book_html(book_id, outline, chapter_bodies)

    out_dir = sample_books_dir() / book_id
    out_dir.mkdir(parents=True, exist_ok=True)
    html_path = out_dir / "book.html"
    pdf_path = out_dir / "book.pdf"
    docx_path = out_dir / "book.docx"

    html_path.write_text(html, encoding="utf-8")
    html_to_pdf(html, pdf_path)
    html_to_docx(html, docx_path)

    # Persist state for Test C (tone variants) and Test D (chapter insert)
    save_book_state(book_id, outline, chapter_bodies)

    legacy_md = out_dir / "book.md"
    if legacy_md.is_file():
        legacy_md.unlink()

    paths = {
        "html": str(html_path.resolve()),
        "pdf": str(pdf_path.resolve()),
        "docx": str(docx_path.resolve()),
    }
    return html, paths
