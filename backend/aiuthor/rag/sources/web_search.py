"""Tavily search API — short answers + page snippets with real URLs."""

from __future__ import annotations

import httpx

from aiuthor.rag.schemas import RawDocument

TAVILY_URL = "https://api.tavily.com/search"


def fetch_tavily_documents(
    query: str,
    *,
    api_key: str,
    max_results: int = 5,
    client: httpx.Client | None = None,
) -> list[RawDocument]:
    own = client is None
    c = client or httpx.Client()
    try:
        r = c.post(
            TAVILY_URL,
            json={
                "api_key": api_key,
                "query": query,
                "search_depth": "basic",
                "include_answer": False,
                "max_results": max_results,
            },
            headers={"Content-Type": "application/json"},
            timeout=45.0,
        )
        r.raise_for_status()
        data = r.json()
        docs: list[RawDocument] = []
        for i, row in enumerate(data.get("results") or []):
            url = row.get("url") or ""
            title = row.get("title") or url or f"result-{i}"
            content = (row.get("content") or "").strip()
            if len(content) < 40:
                continue
            docs.append(
                RawDocument(
                    source_id=f"tavily:{hash(url) & 0xFFFFFFFF:08x}:{i}",
                    title=str(title)[:500],
                    text=content,
                    source_url=url or None,
                    source_type="web",
                )
            )
        return docs
    finally:
        if own:
            c.close()
