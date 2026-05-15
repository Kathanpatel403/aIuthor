"""Wikipedia MediaWiki API — search + plain-text extract (grounded URLs)."""

from __future__ import annotations

import html
import re
from typing import Any

import httpx

from aiuthor.rag.schemas import RawDocument

WIKI_API = "https://{lang}.wikipedia.org/w/api.php"
USER_AGENT = "AIuthorResearchBot/0.1 (educational RAG; contact: local-dev)"


def _clean_extract(raw: str) -> str:
    t = html.unescape(raw)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def wiki_search(client: httpx.Client, lang: str, query: str, limit: int) -> list[dict[str, Any]]:
    r = client.get(
        WIKI_API.format(lang=lang),
        params={
            "action": "query",
            "list": "search",
            "srsearch": query,
            "srlimit": limit,
            "format": "json",
        },
        headers={"User-Agent": USER_AGENT},
        timeout=30.0,
    )
    r.raise_for_status()
    data = r.json()
    return list(data.get("query", {}).get("search", []) or [])


def wiki_extracts_for_titles(
    client: httpx.Client, lang: str, titles: list[str]
) -> dict[str, str]:
    if not titles:
        return {}
    r = client.get(
        WIKI_API.format(lang=lang),
        params={
            "action": "query",
            "format": "json",
            "prop": "extracts",
            "explaintext": 1,
            "exsectionformat": "plain",
            "titles": "|".join(titles),
        },
        headers={"User-Agent": USER_AGENT},
        timeout=30.0,
    )
    r.raise_for_status()
    pages = r.json().get("query", {}).get("pages", {})
    out: dict[str, str] = {}
    for _pid, page in pages.items():
        title = page.get("title")
        ex = page.get("extract")
        if title and ex:
            out[title] = _clean_extract(ex)
    return out


def fetch_wikipedia_documents(
    query: str,
    *,
    lang: str = "en",
    max_articles: int = 2,
    client: httpx.Client | None = None,
) -> list[RawDocument]:
    own = client is None
    c = client or httpx.Client()
    try:
        hits = wiki_search(c, lang, query, max_articles)
        titles = [h["title"] for h in hits if h.get("title")][:max_articles]
        extracts = wiki_extracts_for_titles(c, lang, titles)
        return _build_wiki_docs(lang, titles, extracts)
    finally:
        if own:
            c.close()


def _build_wiki_docs(lang: str, titles: list[str], extracts: dict[str, str]) -> list[RawDocument]:
    from urllib.parse import quote

    docs: list[RawDocument] = []
    for title in titles:
        text = extracts.get(title, "")
        if len(text) < 80:
            continue
        slug = quote(title.replace(" ", "_"), safe="()%")
        url = f"https://{lang}.wikipedia.org/wiki/{slug}"
        docs.append(
            RawDocument(
                source_id=f"wiki:{lang}:{title}",
                title=title,
                text=text,
                source_url=url,
                source_type="wikipedia",
            )
        )
    return docs
