"""Load assembled book artifacts (HTML canonical; legacy markdown supported)."""

from __future__ import annotations

import re
from pathlib import Path

from aiuthor.paths import sample_books_dir

_HTML_CHAPTER = re.compile(
    r'<section[^>]*class="[^"]*chapter[^"]*"[^>]*data-number="(\d+)"[^>]*>'
    r"(.*?)</section>",
    re.DOTALL | re.IGNORECASE,
)
_CHAPTER_TITLE = re.compile(
    r'<span[^>]*class="[^"]*chapter-name[^"]*"[^>]*>(.*?)</span>',
    re.DOTALL | re.IGNORECASE,
)
_CHAPTER_BODY = re.compile(
    r'<div[^>]*class="[^"]*chapter-body[^"]*"[^>]*>(.*)</div>',
    re.DOTALL | re.IGNORECASE,
)


def book_html_path(book_id: str) -> Path:
    return sample_books_dir() / book_id.strip() / "book.html"


def book_legacy_md_path(book_id: str) -> Path:
    return sample_books_dir() / book_id.strip() / "book.md"


def load_book_html(book_id: str) -> tuple[str, Path]:
    path = book_html_path(book_id)
    if path.is_file():
        return path.read_text(encoding="utf-8"), path
    legacy = book_legacy_md_path(book_id)
    if legacy.is_file():
        return legacy.read_text(encoding="utf-8"), legacy
    raise FileNotFoundError(f"No book.html or book.md for book_id={book_id!r}")


def parse_chapters_from_html(html: str) -> list[dict]:
    chapters: list[dict] = []
    for m in _HTML_CHAPTER.finditer(html):
        num = int(m.group(1))
        block = m.group(2)
        title_m = _CHAPTER_TITLE.search(block)
        title = _strip_tags(title_m.group(1)).strip() if title_m else f"Chapter {num}"
        body_m = _CHAPTER_BODY.search(block)
        body_html = body_m.group(1) if body_m else ""
        chapters.append(
            {
                "number": num,
                "title": title,
                "body": _strip_tags(body_html).strip(),
                "body_html": body_html.strip(),
            }
        )
    return chapters


def _strip_tags(fragment: str) -> str:
    text = re.sub(r"(?i)<br\s*/?>", "\n", fragment)
    text = re.sub(r"(?i)</p>", "\n\n", text)
    text = re.sub(r"<[^>]+>", "", text)
    return re.sub(r"\n{3,}", "\n\n", text)


def html_to_plain(html: str) -> str:
    """Plain text for evals / search (strip tags, keep rough paragraph breaks)."""
    text = re.sub(r"(?is)<(script|style).*?>.*?</\1>", "", html)
    text = re.sub(r"(?i)<br\s*/?>", "\n", text)
    text = re.sub(r"(?i)</p>", "\n\n", text)
    text = re.sub(r"(?i)</h[1-6]>", "\n\n", text)
    text = re.sub(r"<[^>]+>", "", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()
