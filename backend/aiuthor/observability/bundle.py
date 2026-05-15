"""Persist trace bundle under traces/{book_id}/."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from aiuthor.observability.context import RunCollector
from aiuthor.observability.token_cost_ledger import ledger_totals
from aiuthor.paths import traces_dir


def save_trace_bundle(collector: RunCollector, *, export_paths: dict[str, str] | None = None) -> dict[str, str]:
    """
    Writes:
      - agent_trace.json
      - prompts.jsonl
      - memory_io.jsonl
      - token_cost_ledger.json
      - manifest.json
    """
    root = traces_dir(collector.book_id)
    root.mkdir(parents=True, exist_ok=True)

    trace_path = root / "agent_trace.json"
    trace_path.write_text(json.dumps({"events": collector.trace_events}, indent=2), encoding="utf-8")

    prompts_path = root / "prompts.jsonl"
    with prompts_path.open("w", encoding="utf-8") as fp:
        for row in collector.prompts:
            fp.write(json.dumps(row, ensure_ascii=False) + "\n")

    mem_path = root / "memory_io.jsonl"
    with mem_path.open("w", encoding="utf-8") as fp:
        for row in collector.memory_io:
            fp.write(json.dumps(row, ensure_ascii=False) + "\n")

    totals = ledger_totals(collector.ledger)
    ledger_path = root / "token_cost_ledger.json"
    ledger_payload = {"entries": collector.ledger, "totals": totals}
    ledger_path.write_text(json.dumps(ledger_payload, indent=2), encoding="utf-8")

    manifest: dict[str, Any] = {
        "run_id": collector.run_id,
        "book_id": collector.book_id,
        "started_at": collector.started_at,
        "files": {
            "agent_trace": str(trace_path),
            "prompts_log": str(prompts_path),
            "memory_io_log": str(mem_path),
            "token_cost_ledger": str(ledger_path),
        },
        "totals": totals,
        "export_paths": export_paths or {},
        "counts": {
            "trace_events": len(collector.trace_events),
            "prompt_turns": len(collector.prompts),
            "memory_io_events": len(collector.memory_io),
            "ledger_entries": len(collector.ledger),
        },
    }
    manifest_path = root / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    return {
        "manifest": str(manifest_path),
        "agent_trace": str(trace_path),
        "prompts_log": str(prompts_path),
        "memory_io_log": str(mem_path),
        "token_cost_ledger": str(ledger_path),
    }


def load_manifest(book_id: str) -> dict[str, Any] | None:
    p = traces_dir(book_id) / "manifest.json"
    if not p.is_file():
        return None
    return json.loads(p.read_text(encoding="utf-8"))
