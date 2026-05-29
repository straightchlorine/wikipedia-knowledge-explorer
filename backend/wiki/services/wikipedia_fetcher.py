"""Wikipedia REST API fetchers backed by a shared lifespan-owned client.

The httpx.AsyncClient is constructed once in `main.lifespan` and registered
here via `set_client`. Calling `fetch_*` before the client is set raises —
that's intentional: it surfaces lifespan-wiring bugs at request time rather
than masking them by silently spinning up a new client per call.
"""

from __future__ import annotations

import httpx

from wiki.settings import get_settings

_client: httpx.AsyncClient | None = None


def set_client(client: httpx.AsyncClient | None) -> None:
    """Register the shared client (call from FastAPI lifespan)."""
    global _client
    _client = client


def _get_client() -> httpx.AsyncClient:
    if _client is None:
        raise RuntimeError(
            "wikipedia_fetcher shared httpx client is not initialized; "
            "the FastAPI lifespan must call set_client() at startup."
        )
    return _client


async def fetch_wikipedia_articles(query: str, max_results: int = 5):
    """Fetch relevant article titles and their page IDs from Wikipedia."""
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "format": "json",
        "utf8": 1,
        "srlimit": max_results,
    }

    response = await _get_client().get(str(get_settings().wikipedia_api_url), params=params)
    response.raise_for_status()
    data = response.json()

    return [
        {"title": item["title"], "pageid": item["pageid"]}
        for item in data.get("query", {}).get("search", [])
    ]


async def fetch_article_content(pageid: int) -> str:
    """Fetch the full content of a Wikipedia article using its page ID."""
    params = {
        "action": "query",
        "pageids": pageid,
        "prop": "extracts",
        "explaintext": True,
        "format": "json",
    }

    response = await _get_client().get(str(get_settings().wikipedia_api_url), params=params)
    response.raise_for_status()
    data = response.json()

    return data["query"]["pages"].get(str(pageid), {}).get("extract", "")
