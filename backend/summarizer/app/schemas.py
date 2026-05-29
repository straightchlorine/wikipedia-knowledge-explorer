"""Wire-protocol schemas for POST /summarize.

These are the contract the API pod (SummarizerClient) consumes — keep
them stable; breaking changes require a coordinated rollout with
backend/wiki/services/summarizer_client.py.
"""

from pydantic import BaseModel, Field


class SummarizeRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=50_000)
    max_length: int = Field(default=130, ge=10, le=512)
    min_length: int = Field(default=30, ge=1, le=256)


class SummarizeResponse(BaseModel):
    summary: str
    model: str
    revision: str
