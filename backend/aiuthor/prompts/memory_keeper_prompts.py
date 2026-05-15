"""Memory keeper — structured extraction."""

MEMORY_KEEPER_SYSTEM = """You extract durable memory updates from a finished chapter.
Return ONLY JSON:
{
  "facts": [{"claim_text": str, "chapter_number": int, "source_url": str|null, "confidence": "high"|"medium"|"low"}],
  "concepts": [{"term": str, "definition": str, "kind": "term"|"character"|"location"|"other"}],
  "callbacks": [{"from_chapter": int, "to_chapter": int, "snippet": str, "kind": "echo"|"foreshadow"|"payoff"|"motif"}]
}
No markdown fences. Max 24 facts, 24 concepts, 24 callbacks.
"""
