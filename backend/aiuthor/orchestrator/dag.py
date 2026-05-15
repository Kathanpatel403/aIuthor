"""LangGraph DAG: Planner → chapter loop → Assembler."""

from __future__ import annotations

try:
    from langgraph.constants import START
except ImportError:  # pragma: no cover
    START = "__start__"

from langgraph.graph import END, StateGraph

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
    graph = build_book_graph()
    initial = {"book_id": book_id, "brief": brief_dict}
    return graph.invoke(initial)
