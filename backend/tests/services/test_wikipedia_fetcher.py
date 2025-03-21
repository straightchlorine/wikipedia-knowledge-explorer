import pytest
import httpx
from unittest.mock import patch, MagicMock
from wiki.services.wikipedia_fetcher import fetch_wikipedia_articles


async def test_fetch_wikipedia_articles_success():
    """Test successful API call to Wikipedia."""

    # mock response object
    mock_response = MagicMock()
    mock_response.status_code = 200

    # example response from the Wikipedia API
    mock_response.json.return_value = {
        "query": {
            "search": [
                {"title": "Python (programming language)"},
                {"title": "Python"},
            ]
        }
    }

    # path the async client to get the mock response
    with patch("httpx.AsyncClient.get", return_value=mock_response):
        result = await fetch_wikipedia_articles("python")

    assert ["Python (programming language)", "Python"] == result
    assert len(result) == 2


async def test_fetch_wikipedia_articles_error():
    """Test handling of API errors."""

    # try to trigger an exception
    with patch(
        "httpx.AsyncClient.get",
        side_effect=httpx.HTTPStatusError(
            "Error", request=MagicMock(), response=MagicMock()
        ),
    ):
        with pytest.raises(httpx.HTTPStatusError):
            await fetch_wikipedia_articles("python")
