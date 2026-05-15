"""Five tonality presets — vocabulary, rhythm, hooks, second-person (Phase 4)."""

from __future__ import annotations

from typing import Literal, TypedDict

TonalityId = Literal["conversational", "academic", "storyteller", "motivational", "witty"]


class TonalityPresetConfig(TypedDict):
    label: str
    second_person_ok: bool
    rhythm_notes: str
    vocabulary: str
    hook_style: str
    banned_softeners: str
    example_openings: list[str]


TONALITY_PRESETS: dict[TonalityId, TonalityPresetConfig] = {
    "conversational": {
        "label": "Conversational",
        "second_person_ok": True,
        "rhythm_notes": "Mix short and medium sentences; contractions welcome; occasional direct question to reader.",
        "vocabulary": "Plain English; concrete verbs; avoid Latinate stacks.",
        "hook_style": "Relatable scene, tension, or misconception corrected quickly.",
        "banned_softeners": "Avoid hedging stacks ('it might perhaps seem that').",
        "example_openings": [
            "You have probably stared at a budget spreadsheet and quietly closed the tab.",
            "Let us start where money actually hits your life: the week after payday.",
        ],
    },
    "academic": {
        "label": "Academic",
        "second_person_ok": False,
        "rhythm_notes": "Longer information-dense sentences; defined terms on first use.",
        "vocabulary": "Precise terminology; neutral stance; cite mechanisms not vibes.",
        "hook_style": "Problem statement + scope + method preview.",
        "banned_softeners": "No faux-informality; no rhetorical questions unless analytically motivated.",
        "example_openings": [
            "This chapter examines how liquidity constraints shape household saving behavior.",
            "We define the key constructs before evaluating empirical regularities.",
        ],
    },
    "storyteller": {
        "label": "Storyteller",
        "second_person_ok": True,
        "rhythm_notes": "Scene beats; sensory detail sparingly; dialogue fragments allowed.",
        "vocabulary": "Concrete nouns; strong verbs; metaphor grounded in the domain.",
        "hook_style": "Character beat or turning point; time and place anchored early.",
        "banned_softeners": "No self-help clichés; no narrator apologizing for telling a story.",
        "example_openings": [
            "The envelope sat unopened on the counter longer than the milk lasted.",
            "Maya learned the hard way that interest is a quiet roommate.",
        ],
    },
    "motivational": {
        "label": "Motivational",
        "second_person_ok": True,
        "rhythm_notes": "Declarative energy; cadence that lands on verbs of agency.",
        "vocabulary": "Action-forward; avoid toxic positivity; credit effort and systems.",
        "hook_style": "Name the obstacle, then a believable pivot the reader can execute this week.",
        "banned_softeners": "No empty superlatives; no shame-as-fuel.",
        "example_openings": [
            "You do not need perfect discipline. You need a plan that survives a bad Tuesday.",
            "Small wins compound when the system is boring enough to repeat.",
        ],
    },
    "witty": {
        "label": "Witty",
        "second_person_ok": True,
        "rhythm_notes": "Quick pivots; controlled irony; never punch down at the reader.",
        "vocabulary": "Unexpected comparisons; crisp one-liners; clarity beats cleverness.",
        "hook_style": "Paradox or wry observation that still earns trust.",
        "banned_softeners": "No snark about vulnerable groups; no meme-speak overload.",
        "example_openings": [
            "Budgets are just gossip columns for your money—spicy, occasionally wrong, still addictive.",
            "If your savings account were a houseplant, honesty demands we ask how long it has been dry.",
        ],
    },
}


def normalize_tonality(value: str) -> TonalityId:
    v = value.strip().lower()
    if v not in TONALITY_PRESETS:
        return "conversational"
    return v  # type: ignore[return-value]
