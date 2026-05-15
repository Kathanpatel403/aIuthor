"""LangGraph node functions (Planner → chapter loop → Assembler)."""

from __future__ import annotations

from aiuthor.agents.assembler import run_assembler
from aiuthor.agents.editor import run_editor
from aiuthor.agents.fact_checker import run_fact_checker
from aiuthor.agents.humanizer import run_humanizer
from aiuthor.agents.memory_keeper import run_memory_keeper
from aiuthor.agents.planner import run_planner
from aiuthor.agents.researcher import run_researcher
from aiuthor.agents.writer import run_writer
from aiuthor.config.settings import get_settings
from aiuthor.observability.agent_tracer import trace_span
from aiuthor.observability.context import set_current_agent
from aiuthor.schemas.brief import BookOutline, UserBrief


def planner_node(state: dict) -> dict:
    brief = UserBrief.model_validate(state["brief"])
    settings = get_settings()
    set_current_agent("planner")
    with trace_span("planner"):
        outline = run_planner(brief, settings)
    return {
        "outline": outline.model_dump(),
        "chapter_index": 0,
        "chapter_bodies": [],
        "artifacts": [],
    }


def chapter_node(state: dict) -> dict:
    settings = get_settings()
    brief = UserBrief.model_validate(state["brief"])
    book_id = state["book_id"]
    outline = BookOutline.model_validate(state["outline"])
    ix = int(state.get("chapter_index", 0))
    ch = outline.chapters[ix]

    set_current_agent("researcher")
    with trace_span("researcher", {"chapter": ch.number}):
        pack = run_researcher(book_id, ch, settings)

    set_current_agent("writer")
    with trace_span("writer", {"chapter": ch.number}):
        raw = run_writer(
            outline.title,
            brief.genre,
            ch,
            pack,
            brief.tonality,
            brief.words_per_chapter,
            settings,
        )

    set_current_agent("humanizer")
    with trace_span("humanizer", {"chapter": ch.number}):
        hum = run_humanizer(raw, brief.tonality, settings)

    set_current_agent("editor")
    with trace_span("editor", {"chapter": ch.number}):
        edited = run_editor(book_id, ch.number, hum, brief.tonality, settings)

    set_current_agent("fact_checker")
    with trace_span("fact_checker", {"chapter": ch.number}):
        checked = run_fact_checker(edited, pack, settings)

    set_current_agent("memory_keeper")
    with trace_span("memory_keeper", {"chapter": ch.number}):
        run_memory_keeper(book_id, ch.number, checked, brief.tonality, settings)

    bodies = list(state.get("chapter_bodies", []))
    bodies.append(checked)
    return {"chapter_index": ix + 1, "chapter_bodies": bodies}


def assemble_node(state: dict) -> dict:
    settings = get_settings()
    outline = BookOutline.model_validate(state["outline"])
    book_id = state["book_id"]
    bodies = list(state.get("chapter_bodies", []))
    set_current_agent("assembler")
    with trace_span("assembler"):
        paths = run_assembler(book_id, outline, bodies, settings)
    from pathlib import Path

    md = Path(paths["markdown"]).read_text(encoding="utf-8")
    return {"export_paths": paths, "assembled_markdown": md}


def route_after_chapter(state: dict) -> str:
    outline = BookOutline.model_validate(state["outline"])
    if state.get("chapter_index", 0) < len(outline.chapters):
        return "chapter"
    return "assemble"
