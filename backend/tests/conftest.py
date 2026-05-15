"""Session-wide test fixtures.

Provide a default `WIKIPEDIA_API_URL` for tests that import `wiki.main` or
`wiki.services.wikipedia_fetcher` indirectly. Individual tests can override
via `monkeypatch.setenv(...)` before constructing `Settings()` directly.
"""

from __future__ import annotations

import os

os.environ.setdefault("WIKIPEDIA_API_URL", "https://en.wikipedia.org/w/api.php")
