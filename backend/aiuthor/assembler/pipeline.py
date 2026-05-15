"""Glue front matter, body, back matter; write PDF + DOCX."""

from __future__ import annotations

from pathlib import Path

from aiuthor.assembler.back_matter import static_back_matter
from aiuthor.assembler.body import body_markdown
from aiuthor.assembler.docx_builder import markdownish_to_docx
from aiuthor.assembler.front_matter import static_front_matter_skeleton, toc_from_chapters
from aiuthor.assembler.pdf_builder import markdownish_to_pdf
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
    Returns (full_markdown, paths{"markdown","pdf","docx"}).
    """
    chapters_meta = [(c.number, c.title) for c in outline.chapters]
    toc = toc_from_chapters(chapters_meta)
    front = static_front_matter_skeleton(outline.title).replace("<!--TOC_PLACEHOLDER-->", toc.strip())
    body = body_markdown(
        [(c.number, c.title, chapter_bodies[i]) for i, c in enumerate(outline.chapters)]
    )
    back = static_back_matter(outline.title, book_id)
    full = "\n\n".join([front, body, back])

    out_dir = sample_books_dir() / book_id
    out_dir.mkdir(parents=True, exist_ok=True)
    md_path = out_dir / "book.md"
    pdf_path = out_dir / "book.pdf"
    docx_path = out_dir / "book.docx"
    md_path.write_text(full, encoding="utf-8")
    markdownish_to_pdf(full, pdf_path)
    markdownish_to_docx(full, docx_path)
    paths = {"markdown": str(md_path), "pdf": str(pdf_path), "docx": str(docx_path)}
    return full, paths
