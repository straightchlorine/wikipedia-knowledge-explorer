from fastapi import APIRouter, HTTPException, Query
from wiki.services.wikipedia_fetcher import fetch_wikipedia_articles

router = APIRouter(prefix="/articles", tags=["articles"])


@router.get("/")
async def search_articles(
    query: str = Query(
        ..., title="Search Term", description="Keyword to search Wikipedia"
    ),
):
    """
    Fetch Wikipedia article titles based on a search term.
    """
    try:
        articles = await fetch_wikipedia_articles(query)
        return {"query": query, "articles": articles}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
