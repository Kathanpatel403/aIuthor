"""Fetch persisted observability bundles."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from aiuthor.observability.bundle import load_manifest
from aiuthor.paths import traces_dir

router = APIRouter()


@router.get("/{book_id}")
def trace_bundle_summary(book_id: str) -> dict:
    """Return manifest.json contents plus lightweight file stats."""
    bid = book_id.strip()
    if not bid:
        raise HTTPException(status_code=400, detail="book_id required")
    manifest = load_manifest(bid)
    if manifest is None:
        raise HTTPException(status_code=404, detail="No trace bundle found for this book_id")
    root = traces_dir(bid)
    stats: dict[str, int | None] = {}
    for label, rel in [
        ("agent_trace", "agent_trace.json"),
        ("prompts_log", "prompts.jsonl"),
        ("memory_io_log", "memory_io.jsonl"),
        ("token_cost_ledger", "token_cost_ledger.json"),
    ]:
        p = root / rel
        stats[label] = p.stat().st_size if p.is_file() else None
    return {"manifest": manifest, "file_sizes_bytes": stats}
