from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel

class LeadSchema(BaseModel):
    id: int | str
    post_id: str
    subreddit: str
    title: str
    body: str | None
    author: str | None
    url: str | None
    upvotes: int | None = 0
    score: int | None = 0
    intents: str | None
    matched_keywords: str | None
    ai_analysis: str | None
    ai_outreach: str | None
    status: str | None = "new"
    notified: bool | None = False
    found_at: datetime
    updated_at: datetime

class LeadListResponse(BaseModel):
    items: list[LeadSchema]
    total: int
    page: int
    page_size: int

class UpdateLeadRequest(BaseModel):
    status: str | None = None

class LeadMutationResponse(BaseModel):
    id: int | str
