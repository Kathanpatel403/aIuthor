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
from aiuthor.schemas.brief import BookOutline, UserBrief


def planner_node(state: dict) -> dict:
    brief = UserBrief.model_validate(state["brief"])
    settings = get_settings()
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
    pack = run_researcher(book_id, ch, settings)
    raw = run_writer(
        outline.title,
        brief.genre,
        ch,
        pack,
        brief.tonality,
        brief.words_per_chapter,
        settings,
    )
    hum = run_humanizer(raw, brief.tonality, settings)
    edited = run_editor(book_id, ch.number, hum, brief.tonality, settings)
    checked = run_fact_checker(edited, pack, settings)
    run_memory_keeper(book_id, ch.number, checked, brief.tonality, settings)
    bodies = list(state.get("chapter_bodies", []))
    bodies.append(checked)
    return {"chapter_index": ix + 1, "chapter_bodies": bodies}


def assemble_node(state: dict) -> dict:
    settings = get_settings()
    outline = BookOutline.model_validate(state["outline"])
    book_id = state["book_id"]
    bodies = list(state.get("chapter_bodies", []))
    paths = run_assembler(book_id, outline, bodies, settings)
    # Re-read assembled markdown from disk for API convenience
    from pathlib import Path

    md = Path(paths["markdown"]).read_text(encoding="utf-8")
    return {"export_paths": paths, "assembled_markdown": md}


def route_after_chapter(state: dict) -> str:
    outline = BookOutline.model_validate(state["outline"])
    if state.get("chapter_index", 0) < len(outline.chapters):
        return "chapter"
    return "assemble"
