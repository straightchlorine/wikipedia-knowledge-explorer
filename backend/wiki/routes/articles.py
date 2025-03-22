import asyncio

from fastapi import APIRouter, HTTPException, Path, Query

from wiki.services.clustering import cluster_articles
from wiki.services.wikipedia_fetcher import (
    fetch_article_content,
    fetch_wikipedia_articles,
)

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
        titles = [article["title"] for article in articles]
        return {"query": query, "articles": titles}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/content/{page_id}")
async def get_article_content(
    page_id: int = Path(
        ...,
        title="Page ID",
        description="Wikipedia page ID to fetch content for",
    ),
):
    """
    Fetch the full content of a Wikipedia article using its page ID.

    Args:
        page_id (int): The Wikipedia page ID to fetch content for

    Returns:
        A JSON object containing the article's page ID and its contents
    """
    try:
        content = await fetch_article_content(page_id)
        return {"pageid": page_id, "content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/clusters")
async def cluster_articles_endpoint(
    query: str = Query(
        ..., title="Search Term", description="Keyword to search Wikipedia"
    ),
):
    """
    Fetch Wikipedia articles, retrieve their full content, and cluster them
    using vectorization and K-Means.

    Returns the articles along with their assigned cluster labels.
    """
    try:
        # get the articles with title and pageid
        articles = await fetch_wikipedia_articles(query)

        # fetch contents for each article concurrently
        tasks = [fetch_article_content(article["pageid"]) for article in articles]
        contents = await asyncio.gather(*tasks)

        # convert articles to tf-idf vectors and cluster them
        labels = cluster_articles(contents, max_clusters=10)

        # attach cluster labels to each article in the result
        for i, article in enumerate(articles):
            article["cluster"] = int(labels[i])

        return {"query": query, "articles": articles}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
