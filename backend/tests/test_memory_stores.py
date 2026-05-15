import pytest

from aiuthor.memory import (
    CallbackIndex,
    ConceptBible,
    DecisionLog,
    FactRegistry,
    TonalityFingerprint,
    repair_after_chapter_insert,
)
from aiuthor.memory.schemas import TonalitySurfaceRecord
from aiuthor.memory.store import reset_memory_store_for_tests


@pytest.fixture(autouse=True)
def _clean_store():
    reset_memory_store_for_tests()
    yield
    reset_memory_store_for_tests()


def test_fact_registry_roundtrip():
    fr = FactRegistry("book-1")
    fr.add_fact(chapter_number=2, claim_text="Compound interest grows savings.")
    assert len(fr.list_all()) == 1
    assert fr.list_for_chapter(2)[0].claim_text.startswith("Compound")


def test_concept_bible_upsert():
    cb = ConceptBible("book-1")
    cb.add_concept(term="401(k)", definition="Tax-advantaged retirement account.", first_mentioned_chapter=3)
    cb.add_concept(term="401(k)", definition="Updated definition.", first_mentioned_chapter=3)
    assert len(cb.list_all()) == 1
    assert cb.list_all()[0].definition == "Updated definition."


def test_callback_index_repair_shifts():
    ix = CallbackIndex("book-1")
    ix.add_callback(from_chapter=5, to_chapter=7, snippet="As we saw in budgeting…")
    ix.add_callback(from_chapter=2, to_chapter=5, snippet="Sets up chapter 5 payoff.")
    touched = ix.trigger_repair_after_chapter_insert(4)
    assert touched == 3  # three field bumps across two rows
    rows = ix.list_all()
    assert {(r.from_chapter, r.to_chapter) for r in rows} == {(2, 6), (6, 8)}


def test_full_repair_pipeline_counts():
    bid = "book-repair"
    FactRegistry(bid).add_fact(chapter_number=5, claim_text="Old chapter 5 fact")
    ConceptBible(bid).add_concept(term="Snowball", definition="Debt payoff method", first_mentioned_chapter=6)
    CallbackIndex(bid).add_callback(from_chapter=5, to_chapter=6, snippet="link")
    report = repair_after_chapter_insert(bid, insert_after_chapter=4)
    assert report.shifted_facts == 1
    assert report.shifted_concepts == 1
    assert report.shifted_callbacks == 2


def test_decision_log_append_only():
    log = DecisionLog("book-1")
    log.append_event(agent="planner", action="outline_v1", details={"chapters": 10})
    assert len(log.list_all()) == 1
    assert log.list_all()[0].agent == "planner"


def test_tonality_fingerprint_surface():
    fp = TonalityFingerprint("book-1")
    fp.set_surface(
        TonalitySurfaceRecord(surface="preface", embedding=[0.1, 0.2], exemplar_text="Warm opener.")
    )
    assert fp.get_surface("preface") is not None
    assert fp.get_surface("preface").exemplar_text == "Warm opener."
