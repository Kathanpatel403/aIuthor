"""Repository paths (demo_gateway root = parent of backend/)."""

from __future__ import annotations

from pathlib import Path

_AIUTHOR_PKG = Path(__file__).resolve().parent
REPO_ROOT: Path = _AIUTHOR_PKG.parent.parent


def sample_books_dir() -> Path:
    return REPO_ROOT / "sample_books"


def traces_dir(book_id: str) -> Path:
    return REPO_ROOT / "traces" / book_id


def memory_data_dir() -> Path:
    """Directory for optional JSON snapshots of the in-memory book memory store."""
    d = REPO_ROOT / "memory_data"
    d.mkdir(parents=True, exist_ok=True)
    return d
