"""LangGraph shared state (dict-serializable for JSON boundaries)."""

from __future__ import annotations

from typing import Any, TypedDict


class BookPipelineState(TypedDict, total=False):
    book_id: str
    brief: dict[str, Any]
    outline: dict[str, Any] | None
    chapter_index: int
    chapter_bodies: list[str]
    artifacts: list[dict[str, Any]]
    errors: list[str]
    export_paths: dict[str, str]
    assembled_html: str
    trace_bundle_paths: dict[str, str]
