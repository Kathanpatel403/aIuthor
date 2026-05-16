"""PDF export from HTML (WeasyPrint preferred; xhtml2pdf fallback)."""

from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def html_to_pdf(html: str, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if _weasyprint_pdf(html, out_path):
        return
    if _xhtml2pdf(html, out_path):
        return
    raise RuntimeError(
        "PDF export failed: install weasyprint (recommended) or xhtml2pdf. "
        "See backend/requirements.txt."
    )


def _weasyprint_pdf(html: str, out_path: Path) -> bool:
    try:
        from weasyprint import HTML
    except ImportError:
        return False
    try:
        HTML(string=html, base_url=str(out_path.parent.resolve())).write_pdf(str(out_path))
        return True
    except Exception as exc:  # noqa: BLE001
        logger.warning("WeasyPrint PDF failed (%s), trying fallback", exc)
        return False


def _xhtml2pdf(html: str, out_path: Path) -> bool:
    try:
        from xhtml2pdf import pisa
    except ImportError:
        return False
    with open(out_path, "wb") as dest:
        status = pisa.CreatePDF(html, dest=dest, encoding="utf-8")
    if status.err:
        logger.warning("xhtml2pdf reported errors for %s", out_path)
    return out_path.is_file() and out_path.stat().st_size > 0


def markdownish_to_pdf(text: str, out_path: Path) -> None:
    """Legacy wrapper: wrap plain text in minimal HTML."""
    escaped = (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
    blocks = "".join(f"<p>{line}</p>" for line in escaped.split("\n\n") if line.strip())
    html = (
        "<!DOCTYPE html><html><head><meta charset='utf-8'/>"
        "<style>body{font-family:Georgia,serif;font-size:11pt;line-height:1.5;margin:2cm;}</style>"
        f"</head><body>{blocks}</body></html>"
    )
    html_to_pdf(html, out_path)
