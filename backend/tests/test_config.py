import os
import importlib
import wiki.config


def test_config_uses_default_url():
    """Test config uses default URL when environment variable is not set."""
    if "WIKIPEDIA_API_URL" not in os.environ:
        assert wiki.config.WIKIPEDIA_API_URL == "https://en.wikipedia.org/w/api.php"


def test_config_uses_environment_variable(monkeypatch):
    """Test config uses environment variable when set."""

    # set the temporary environment variable
    monkeypatch.setenv("WIKIPEDIA_API_URL", "https://test.wikipedia.org/w/api.php")
    importlib.reload(wiki.config)

    assert wiki.config.WIKIPEDIA_API_URL == "https://test.wikipedia.org/w/api.php"
