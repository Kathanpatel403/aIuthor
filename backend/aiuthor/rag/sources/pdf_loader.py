"""Load plain text from user-uploaded PDFs (PyPDF)."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

from pypdf import PdfReader

from aiuthor.rag.schemas import RawDocument


def pdf_bytes_to_text(data: bytes) -> str:
    reader = PdfReader(BytesIO(data))
    parts: list[str] = []
    for page in reader.pages:
        t = page.extract_text() or ""
        parts.append(t)
    return "\n\n".join(parts).strip()


def load_pdf_document(
    path: str | Path,
    *,
    source_id: str | None = None,
    title: str | None = None,
) -> RawDocument:
    p = Path(path)
    raw = p.read_bytes()
    text = pdf_bytes_to_text(raw)
    sid = source_id or f"pdf:{p.stem}"
    ttl = title or p.stem
    return RawDocument(
        source_id=sid,
        title=ttl,
        text=text,
        source_url=f"file://{p.resolve()}",
        source_type="pdf",
    )


def load_pdf_from_bytes(
    data: bytes,
    *,
    source_id: str,
    title: str,
    source_url: str | None = None,
) -> RawDocument:
    text = pdf_bytes_to_text(data)
    return RawDocument(
        source_id=source_id,
        title=title,
        text=text,
        source_url=source_url,
        source_type="pdf",
    )
