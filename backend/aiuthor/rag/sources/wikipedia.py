"""Wikipedia MediaWiki API — search + plain-text extract (grounded URLs).

No API key — uses the public MediaWiki `action=query` endpoint. Requests must send a
descriptive User-Agent (Wikimedia policy); blocks or empty results usually mean network,
rate limits, or extracts shorter than the minimum length filter.
"""

from __future__ import annotations

import html
import logging
import re
from typing import Any

import httpx

from aiuthor.rag.schemas import RawDocument

logger = logging.getLogger(__name__)

WIKI_API = "https://{lang}.wikipedia.org/w/api.php"
# Wikimedia requires a descriptive User-Agent with contact info (URL or email).
# https://meta.wikimedia.org/wiki/User-Agent_policy
USER_AGENT = (
    "AIuthorRAG/1.0 (https://meta.wikimedia.org/wiki/User-Agent_policy; "
    "educational book-generation RAG; no bulk scraping)"
)
# Long srsearch strings often yield 403/414 from upstream; keep requests small.
_WIKI_SEARCH_QUERY_MAX_CHARS = 200
# Very short extracts are often disambiguation stubs — skip below this length.
_MIN_EXTRACT_CHARS = 40


def _clip_wiki_search_query(query: str, max_len: int = _WIKI_SEARCH_QUERY_MAX_CHARS) -> str:
    """Wikipedia search rejects very long query strings; prefer a short, title-like prefix."""
    q = query.strip()
    if len(q) <= max_len:
        return q
    cut = q[:max_len]
    for sep in (". ", " — ", " - ", "\n"):
        i = cut.rfind(sep)
        if i >= 40:
            return cut[:i].strip()
    return cut.rstrip() + "..."


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
    c = client or httpx.Client(follow_redirects=True)
    search_q = _clip_wiki_search_query(query)
    if search_q != query.strip():
        logger.info(
            "wikipedia search query clipped from %d to %d chars (upstream limits)",
            len(query.strip()),
            len(search_q),
        )
    try:
        try:
            hits = wiki_search(c, lang, search_q, max_articles)
        except httpx.HTTPStatusError as exc:
            code = exc.response.status_code
            if code in (400, 403, 414, 429):
                logger.warning(
                    "Wikipedia search HTTP %s (lang=%s query_prefix=%r)",
                    code,
                    lang,
                    search_q[:120],
                )
                return []
            raise
        if not hits:
            logger.info("wikipedia search returned no hits query=%r lang=%s", search_q[:120], lang)
        titles = [h["title"] for h in hits if h.get("title")][:max_articles]
        extracts = wiki_extracts_for_titles(c, lang, titles)
        docs = _build_wiki_docs(lang, titles, extracts)
        if not docs and max_articles > 0:
            logger.info(
                "wikipedia produced zero usable docs (titles=%s extracts_keys=%s) query=%r",
                titles,
                list(extracts.keys()),
                search_q[:120],
            )
        return docs
    finally:
        if own:
            c.close()


def _build_wiki_docs(lang: str, titles: list[str], extracts: dict[str, str]) -> list[RawDocument]:
    from urllib.parse import quote

    docs: list[RawDocument] = []
    for title in titles:
        text = extracts.get(title, "")
        if len(text) < _MIN_EXTRACT_CHARS:
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
