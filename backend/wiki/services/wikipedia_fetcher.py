import httpx
from wiki.config import WIKIPEDIA_API_URL


async def fetch_wikipedia_articles(query: str):
    """
    Fetch relevant article titles from Wikipedia using the API.
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

    articles = [item["title"] for item in data["query"]["search"]]
    return articles
