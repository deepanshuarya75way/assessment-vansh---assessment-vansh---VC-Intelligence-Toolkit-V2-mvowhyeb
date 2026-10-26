from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class CandidateCreate(BaseModel):
    company: str
    description: str
    source: str | None = None
    github_url: str | None = None
    similarity_score: float | None = None
    portfolio_matches: list[dict[str, Any]] | None = None
    confidence: float | None = None
    reasoning: str | None = None


class CandidateOut(CandidateCreate):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
