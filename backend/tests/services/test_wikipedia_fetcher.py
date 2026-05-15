from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from wiki.services import wikipedia_fetcher
from wiki.services.wikipedia_fetcher import fetch_article_content, fetch_wikipedia_articles


@pytest.fixture
def mock_client():
    """Install a fake shared httpx client for the duration of one test."""
    client = MagicMock()
    client.get = AsyncMock()
    wikipedia_fetcher.set_client(client)
    yield client
    wikipedia_fetcher.set_client(None)


async def test_fetch_wikipedia_articles_success(mock_client):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "query": {
            "search": [
                {"title": "Python (programming language)", "pageid": "1234"},
                {"title": "Python", "pageid": "5678"},
            ]
        }
    }
    mock_response.raise_for_status = MagicMock()
    mock_client.get.return_value = mock_response

    result = await fetch_wikipedia_articles("python")

    assert [x["title"] for x in result] == ["Python (programming language)", "Python"]
    assert len(result) == 2


async def test_fetch_wikipedia_articles_error(mock_client):
    mock_client.get.side_effect = httpx.HTTPStatusError(
        "Error", request=MagicMock(), response=MagicMock()
    )
    with pytest.raises(httpx.HTTPStatusError):
        await fetch_wikipedia_articles("python")


async def test_fetch_article_content_success(mock_client):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "query": {"pages": {"123": {"extract": "Article content"}}}
    }
    mock_response.raise_for_status = MagicMock()
    mock_client.get.return_value = mock_response

    result = await fetch_article_content(123)
    assert result == "Article content"


async def test_fetch_article_content_missing_page(mock_client):
    mock_response = MagicMock()
    mock_response.json.return_value = {"query": {"pages": {}}}
    mock_response.raise_for_status = MagicMock()
    mock_client.get.return_value = mock_response

    result = await fetch_article_content(999)
    assert result == ""


async def test_fetch_raises_when_client_not_initialized():
    """Calling a fetcher without lifespan init is a wiring bug; surface it."""
    wikipedia_fetcher.set_client(None)
    with pytest.raises(RuntimeError, match="not initialized"):
        await fetch_wikipedia_articles("python")
