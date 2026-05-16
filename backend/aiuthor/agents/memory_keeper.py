"""Memory keeper → in-memory stores (OpenAI chat JSON)."""

from __future__ import annotations

import json
import re
import uuid

from aiuthor.config.settings import Settings
from aiuthor.memory import CallbackIndex, ConceptBible, DecisionLog, FactRegistry
from aiuthor.memory.schemas import CallbackRecord, FactRecord, TonalitySurfaceRecord
from aiuthor.memory.tonality_fingerprint import TonalityFingerprint
from aiuthor.orchestrator.llm import completion_text, openai_client
from aiuthor.prompts.memory_keeper_prompts import MEMORY_KEEPER_SYSTEM
from aiuthor.rag.embeddings import embed_texts


def run_memory_keeper(
    book_id: str,
    chapter_number: int,
    chapter_text: str,
    tonality: str,
    settings: Settings,
) -> None:
    if not settings.openai_api_key:
        return
    client = openai_client(settings)
    raw = completion_text(
        client,
        model=settings.openai_chat_model_mini,
        system=MEMORY_KEEPER_SYSTEM,
        user=f"chapter_number={chapter_number}\n\nCHAPTER_TEXT:\n{chapter_text[:24000]}",
        max_tokens=4096,
        temperature=0.1,
        agent="memory_keeper",
        settings=settings,
    )
    m = re.search(r"\{[\s\S]*\}", raw)
    if not m:
        return
    data = json.loads(m.group(0))
    fr = FactRegistry(book_id)
    cb = ConceptBible(book_id)
    ix = CallbackIndex(book_id)
    log = DecisionLog(book_id)
    for f in data.get("facts") or []:
        try:
            conf = f.get("confidence", "medium")
            if conf not in ("high", "medium", "low"):
                conf = "medium"
            fr.append(
                FactRecord(
                    id=str(uuid.uuid4()),
                    chapter_number=int(f.get("chapter_number", chapter_number)),
                    claim_text=str(f.get("claim_text", ""))[:2000],
                    source_url=f.get("source_url"),
                    confidence=conf,  # type: ignore[arg-type]
                )
            )
        except Exception:
            continue
    for c in data.get("concepts") or []:
        try:
            kind = c.get("kind", "term")
            if kind not in ("term", "character", "location", "other"):
                kind = "term"
            cb.add_concept(
                term=str(c.get("term", "term"))[:500],
                definition=str(c.get("definition", ""))[:4000],
                first_mentioned_chapter=chapter_number,
                kind=kind,  # type: ignore[arg-type]
            )
        except Exception:
            continue
    for c in data.get("callbacks") or []:
        try:
            ckind = c.get("kind", "echo")
            if ckind not in ("echo", "foreshadow", "payoff", "motif"):
                ckind = "echo"
            ix.append(
                CallbackRecord(
                    id=str(uuid.uuid4()),
                    from_chapter=int(c.get("from_chapter", chapter_number)),
                    to_chapter=int(c["to_chapter"]),
                    snippet=str(c.get("snippet", ""))[:2000],
                    kind=ckind,  # type: ignore[arg-type]
                )
            )
        except Exception:
            continue
    log.append_event(
        agent="memory_keeper",
        action="chapter_commit",
        details={"chapter": chapter_number, "tonality": tonality},
    )

    # Tonality fingerprint (Phase 4) — embed first ~600 chars of chapter body surface
    if settings.openai_api_key:
        try:
            sample = chapter_text[:600].strip()
            if sample:
                vec = embed_texts([sample], settings=settings)[0]
                TonalityFingerprint(book_id).set_surface(
                    TonalitySurfaceRecord(
                        surface=f"chapter_body:{chapter_number}",
                        embedding=vec,
                        exemplar_text=sample[:400],
                    )
                )
        except Exception:
            pass
