"""Book preview + export URLs for Phase 8 frontend."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, Request

from aiuthor.api.pipeline_jobs import job_get
from aiuthor.assembler.book_io import book_html_path, load_book_html, parse_chapters_from_html
from aiuthor.config.settings import get_settings
from aiuthor.observability.bundle import load_manifest
from aiuthor.paths import sample_books_dir

router = APIRouter()

_CHAPTER_HEADING = re.compile(r"^## Chapter (\d+): (.+)$", re.MULTILINE)


def _parse_body_chapters_markdown(markdown: str) -> list[dict[str, Any]]:
    if "# Body" not in markdown:
        return []
    body = markdown.split("# Body", 1)[1]
    matches = list(_CHAPTER_HEADING.finditer(body))
    if not matches:
        return []
    chapters: list[dict[str, Any]] = []
    for i, m in enumerate(matches):
        num = int(m.group(1))
        title = m.group(2).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        chapters.append({"number": num, "title": title, "body": body[start:end].strip()})
    return chapters


def _export_paths_for_book(book_id: str) -> dict[str, str]:
    job = job_get(book_id)
    if job and job.get("export_paths"):
        paths = {k: v for k, v in dict(job["export_paths"]).items() if k in ("html", "pdf", "docx")}
        if paths:
            return paths
    manifest = load_manifest(book_id)
    if manifest and manifest.get("export_paths"):
        paths = {k: v for k, v in dict(manifest["export_paths"]).items() if k in ("html", "pdf", "docx")}
        if paths:
            return paths
    root = sample_books_dir() / book_id
    out: dict[str, str] = {}
    for key, name in [("html", "book.html"), ("pdf", "book.pdf"), ("docx", "book.docx")]:
        p = root / name
        if p.is_file():
            out[key] = str(p.resolve())
    return out


def _media_download_urls(request: Request, book_id: str) -> dict[str, str]:
    settings = get_settings()
    base = str(request.base_url).rstrip("/")
    prefix = settings.aiuthor_api_prefix.rstrip("/")
    root = f"{base}{prefix}/media/sample-books/{book_id}"
    return {
        "pdf": f"{root}/book.pdf",
        "docx": f"{root}/book.docx",
    }


@router.get("/{book_id}/preview")
def book_preview(book_id: str) -> dict[str, Any]:
    bid = book_id.strip()
    if not bid:
        raise HTTPException(status_code=400, detail="book_id required")
    try:
        content, path = load_book_html(bid)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail="book not found — run the pipeline first (expects sample_books/{id}/book.html)",
        ) from exc

    if path.suffix.lower() == ".html":
        chapters = parse_chapters_from_html(content)
        return {
            "book_id": bid,
            "format": "html",
            "chapters": chapters,
        }

    return {
        "book_id": bid,
        "format": "markdown",
        "markdown": content,
        "chapters": _parse_body_chapters_markdown(content),
    }


@router.get("/{book_id}/exports")
def book_exports(request: Request, book_id: str) -> dict[str, Any]:
    bid = book_id.strip()
    if not bid:
        raise HTTPException(status_code=400, detail="book_id required")
    paths = _export_paths_for_book(bid)
    if not paths.get("pdf") and not (sample_books_dir() / bid / "book.pdf").is_file():
        raise HTTPException(status_code=404, detail="Exports not found for this book_id")
    return {
        "book_id": bid,
        "paths": paths,
        "downloads": _media_download_urls(request, bid),
    }
