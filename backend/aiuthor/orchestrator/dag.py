"""LangGraph DAG: Planner → chapter loop → Assembler."""

from __future__ import annotations

try:
    from langgraph.constants import START
except ImportError:  # pragma: no cover
    START = "__start__"

from langgraph.graph import END, StateGraph

from aiuthor.api.pipeline_jobs import job_complete, job_fail
from aiuthor.observability.context import pipeline_run_context, utc_iso
from aiuthor.orchestrator.graph_nodes import (
    assemble_node,
    chapter_node,
    planner_node,
    route_after_chapter,
)
from aiuthor.orchestrator.state import BookPipelineState


def build_book_graph():
    g = StateGraph(BookPipelineState)
    g.add_node("planner", planner_node)
    g.add_node("chapter", chapter_node)
    g.add_node("assemble", assemble_node)
    g.add_edge(START, "planner")
    g.add_edge("planner", "chapter")
    g.add_conditional_edges(
        "chapter",
        route_after_chapter,
        {"chapter": "chapter", "assemble": "assemble"},
    )
    g.add_edge("assemble", END)
    return g.compile()


def run_book_pipeline(book_id: str, brief_dict: dict) -> dict:
    from aiuthor.observability.bundle import save_trace_bundle

    graph = build_book_graph()
    initial: BookPipelineState = {"book_id": book_id, "brief": brief_dict}
    with pipeline_run_context(book_id) as coll:
        try:
            result = dict(graph.invoke(initial))
        except Exception as exc:  # noqa: BLE001
            coll.trace_events.append(
                {
                    "ts": utc_iso(),
                    "step": "pipeline",
                    "phase": "error",
                    "error": f"{exc.__class__.__name__}: {exc}",
                }
            )
            save_trace_bundle(coll, export_paths={})
            job_fail(book_id, f"{exc.__class__.__name__}: {exc}")
            raise
        bundle_paths = save_trace_bundle(coll, export_paths=result.get("export_paths"))
        result["trace_bundle_paths"] = bundle_paths
        exp = result.get("export_paths") or {}
        if exp:
            job_complete(
                book_id,
                export_paths=dict(exp),
                trace_bundle_paths=dict(bundle_paths),
            )
        return result
