"""Run full eval suite and persist evals_report.json."""

from __future__ import annotations

from aiuthor.config.settings import Settings, get_settings
from aiuthor.evals.ai_tell_detector import ai_tell_score
from aiuthor.evals.callback_recall import callback_recall_score
from aiuthor.evals.fact_coverage import fact_coverage_score
from aiuthor.evals.schemas import DimensionScore, EvalReport
from aiuthor.assembler.book_io import html_to_plain, load_book_html
from aiuthor.evals.structural_check import structural_score, structural_score_html
from aiuthor.evals.tonality_eval import tonality_fidelity_score
from aiuthor.paths import traces_dir


WEIGHTS = {
    "structural": 0.25,
    "tonality": 0.20,
    "ai_tells": 0.20,
    "callbacks": 0.15,
    "fact_coverage": 0.20,
}


def load_book_markdown(book_id: str) -> tuple[str, Path]:
    """Load book text for evals (HTML books converted to plain text)."""
    raw, path = load_book_html(book_id)
    if path.suffix.lower() == ".html":
        return html_to_plain(raw), path
    return raw, path


def run_eval_suite(
    book_id: str,
    *,
    target_tonality: str = "conversational",
    markdown_override: str | None = None,
    settings: Settings | None = None,
) -> EvalReport:
    s = settings or get_settings()
    raw_html: str | None = None
    if markdown_override is not None:
        md = markdown_override
        src = "inline_override"
    else:
        raw, md_path = load_book_html(book_id)
        src = str(md_path)
        if md_path.suffix.lower() == ".html":
            raw_html = raw
            md = html_to_plain(raw)
        else:
            md = raw

    failures: list[str] = []
    if raw_html is not None:
        struct_s, struct_d, missing = structural_score_html(raw_html)
    else:
        struct_s, struct_d, missing = structural_score(md)
    if missing:
        failures.append(f"Missing headings: {', '.join(missing[:10])}")

    tone_s, tone_d = tonality_fidelity_score(md, target_tonality, settings=s)
    ai_s, ai_d = ai_tell_score(md)
    cb_s, cb_d = callback_recall_score(book_id, md)
    fc_s, fc_d = fact_coverage_score(book_id, md)

    dims = [
        DimensionScore(name="structural", score=struct_s, weight=WEIGHTS["structural"], detail=struct_d),
        DimensionScore(name="tonality_fidelity", score=tone_s, weight=WEIGHTS["tonality"], detail=tone_d),
        DimensionScore(name="ai_tell_density", score=ai_s, weight=WEIGHTS["ai_tells"], detail=ai_d),
        DimensionScore(name="callback_recall", score=cb_s, weight=WEIGHTS["callbacks"], detail=cb_d),
        DimensionScore(name="fact_coverage", score=fc_s, weight=WEIGHTS["fact_coverage"], detail=fc_d),
    ]
    overall = sum(d.score * d.weight for d in dims)

    if struct_s < 0.85:
        failures.append("Structural completeness below threshold for submission-ready books.")
    if ai_s < 0.7:
        failures.append("AI-tell detector suggests polish pass on Humanizer.")
    if tone_s < 0.55:
        failures.append("Tonality embedding distance suggests drift from exemplar voice.")

    report = EvalReport(
        book_id=book_id,
        markdown_source=src,
        overall_score=round(overall, 4),
        dimensions=dims,
        failure_analysis=failures,
    )

    out = traces_dir(book_id) / "evals_report.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(report.model_dump_json(indent=2), encoding="utf-8")
    return report
