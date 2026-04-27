from __future__ import annotations
from fastapi import APIRouter
from pydantic import BaseModel
from lead_engine.database import (
    get_active_keywords, set_keywords, 
    get_active_subreddits, set_subreddits,
    get_ai_prompt, set_ai_prompt
)

router = APIRouter(prefix="/config", tags=["config"])

class ConfigResponse(BaseModel):
    keywords: list[str]
    subreddits: list[str]
    ai_prompt: str | None

class UpdateItemsRequest(BaseModel):
    items: list[str]

class UpdatePromptRequest(BaseModel):
    prompt: str

@router.get("", response_model=ConfigResponse)
async def get_config():
    return ConfigResponse(
        keywords=await get_active_keywords(),
        subreddits=await get_active_subreddits(),
        ai_prompt=await get_ai_prompt()
    )

@router.post("/keywords")
async def update_keywords(payload: UpdateItemsRequest):
    await set_keywords(payload.items)
    return {"status": "success"}

@router.post("/subreddits")
async def update_subreddits(payload: UpdateItemsRequest):
    await set_subreddits(payload.items)
    return {"status": "success"}

@router.post("/prompt")
async def update_prompt(payload: UpdatePromptRequest):
    await set_ai_prompt(payload.prompt)
    return {"status": "success"}
