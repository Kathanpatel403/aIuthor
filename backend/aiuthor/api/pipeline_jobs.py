"""In-process pipeline job status for async UI (Phase 8)."""

from __future__ import annotations

import threading
from typing import Any

_lock = threading.Lock()
_jobs: dict[str, dict[str, Any]] = {}


def job_create(book_id: str, brief_summary: dict[str, Any]) -> None:
    with _lock:
        _jobs[book_id] = {
            "book_id": book_id,
            "status": "queued",
            "stage": "queued",
            "chapter_index": 0,
            "total_chapters": None,
            "current_agent": None,
            "error": None,
            "export_paths": None,
            "trace_bundle_paths": None,
            "brief_summary": brief_summary,
        }


def job_update(book_id: str, **kwargs: Any) -> None:
    with _lock:
        if book_id not in _jobs:
            return
        _jobs[book_id].update(kwargs)


def job_get(book_id: str) -> dict[str, Any] | None:
    with _lock:
        j = _jobs.get(book_id)
        return dict(j) if j else None


def job_complete(
    book_id: str,
    *,
    export_paths: dict[str, str],
    trace_bundle_paths: dict[str, str],
) -> None:
    with _lock:
        if book_id not in _jobs:
            return
        _jobs[book_id].update(
            {
                "status": "done",
                "stage": "done",
                "export_paths": export_paths,
                "trace_bundle_paths": trace_bundle_paths,
                "current_agent": None,
            }
        )


def job_fail(book_id: str, message: str) -> None:
    with _lock:
        if book_id not in _jobs:
            return
        _jobs[book_id].update({"status": "error", "stage": "error", "error": message, "current_agent": None})
