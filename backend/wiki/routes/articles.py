import asyncio
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Path
from pydantic import BaseModel, Field
from starlette.requests import Request

from wiki.limits import limiter
from wiki.services.clustering import cluster_articles
from wiki.services.summarizer_client import SummarizerClient
from wiki.services.wikipedia_fetcher import (
    fetch_article_content,
    fetch_wikipedia_articles,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/articles", tags=["articles"])


class SearchParams(BaseModel):
    query: str = Field(
        ...,
        title="Search Term",
        description="Keyword to search Wikipedia",
        min_length=1,
        max_length=200,
    )
    max_results: int = Field(
        5,
        title="Maximum Results",
        description="Maximum number of search results to return",
        ge=1,
        le=50,
    )


SearchParamsDep = Annotated[SearchParams, Depends()]


async def get_summarizer(request: Request) -> SummarizerClient:
    """Return the lifespan-owned SummarizerClient singleton."""
    return request.app.state.summarizer


SummarizerDep = Annotated[SummarizerClient, Depends(get_summarizer)]


@router.get("/")
@limiter.limit("30/minute")
async def search_articles(request: Request, params: SearchParamsDep):
    """
    Fetch Wikipedia article titles based on a search term.
    """
    articles = await fetch_wikipedia_articles(params.query, params.max_results)
    titles = [article["title"] for article in articles]
    return {"query": params.query, "articles": titles}


@router.get("/content/{page_id}")
@limiter.limit("30/minute")
async def get_article_content(
    request: Request,
    page_id: int = Path(
        ...,
        title="Page ID",
        description="Wikipedia page ID to fetch content for",
    ),
):
    """
    Fetch the full content of a Wikipedia article using its page ID.
    """
    content = await fetch_article_content(page_id)
    return {"pageid": page_id, "content": content}


@router.get("/clusters")
@limiter.limit("30/minute")
async def cluster_articles_endpoint(
    request: Request,
    params: SearchParamsDep,
    summarizer: SummarizerDep,
):
    """
    Fetch Wikipedia articles, retrieve their full content, and cluster them
    using vectorization and K-Means.

    Returns the articles along with their assigned cluster labels and summaries.
    """
    articles = await fetch_wikipedia_articles(params.query, params.max_results)

    tasks = [fetch_article_content(article["pageid"]) for article in articles]
    contents = await asyncio.gather(*tasks)

    labels, summaries = await cluster_articles(contents, summarizer, max_clusters=10)

    for i, article in enumerate(articles):
        article["cluster"] = int(labels[i])
        article["summary"] = summaries[i]

    return {"query": params.query, "articles": articles}
