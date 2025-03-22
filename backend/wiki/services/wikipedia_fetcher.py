import httpx

from wiki.config import WIKIPEDIA_API_URL


async def fetch_wikipedia_articles(query: str):
    """
    Fetch relevant article titles and their page IDs from Wikipedia.
    """
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "format": "json",
        "utf8": 1,
        "srlimit": 5,
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(WIKIPEDIA_API_URL, params=params)
        response.raise_for_status()
        data = response.json()

    articles = [
        {"title": item["title"], "pageid": item["pageid"]}
        for item in data["query"]["search"]
    ]
    return articles


async def fetch_article_content(pageid: int):
    """
    Fetch the full content of a Wikipedia article using its page ID.
    """
    params = {
        "action": "query",
        "pageids": pageid,
        "prop": "extracts",
        "explaintext": True,
        "format": "json",
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(WIKIPEDIA_API_URL, params=params)
        response.raise_for_status()
        data = response.json()

    return data["query"]["pages"].get(str(pageid), {}).get("extract", "")
