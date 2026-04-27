import logging
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from lead_engine.config import CONFIG

log = logging.getLogger("leadgen.database")

_client = None

def get_db_client():
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(CONFIG["MONGODB_URI"])
    return _client

def get_db():
    client = get_db_client()
    return client[CONFIG["MONGODB_DB_NAME"]]

async def get_active_keywords() -> list[str]:
    db = get_db()
    doc = await db.config.find_one({"key": "keywords"})
    if doc and doc.get("value"):
        return doc["value"].split(",")
    return []

async def set_keywords(keywords: list[str]):
    db = get_db()
    await db.config.update_one(
        {"key": "keywords"},
        {"$set": {"value": ",".join(keywords)}},
        upsert=True
    )

async def get_active_subreddits() -> list[str]:
    db = get_db()
    doc = await db.config.find_one({"key": "subreddits"})
    if doc and doc.get("value"):
        return doc["value"].split(",")
    return []

async def set_subreddits(subreddits: list[str]):
    db = get_db()
    await db.config.update_one(
        {"key": "subreddits"},
        {"$set": {"value": ",".join(subreddits)}},
        upsert=True
    )

async def get_ai_prompt() -> str | None:
    db = get_db()
    doc = await db.config.find_one({"key": "ai_prompt"})
    return doc.get("value") if doc else None

async def set_ai_prompt(prompt: str):
    db = get_db()
    await db.config.update_one(
        {"key": "ai_prompt"},
        {"$set": {"value": prompt}},
        upsert=True
    )

async def is_post_processed(post_id: str) -> bool:
    db = get_db()
    doc = await db.processed_posts.find_one({"post_id": post_id})
    return doc is not None

async def mark_post_processed(post_id: str):
    db = get_db()
    await db.processed_posts.update_one(
        {"post_id": post_id},
        {"$set": {"processed_at": datetime.now(timezone.utc)}},
        upsert=True
    )

async def load_seen_post_ids() -> set[str]:
    db = get_db()
    cursor = db.leads.find({}, {"post_id": 1})
    ids = set()
    async for doc in cursor:
        ids.add(doc["post_id"])
    return ids

async def save_lead(lead_data: dict):
    db = get_db()
    lead_data["updated_at"] = datetime.now(timezone.utc)
    if "found_at" not in lead_data:
        lead_data["found_at"] = datetime.now(timezone.utc)
    
    await db.leads.update_one(
        {"post_id": lead_data["post_id"]},
        {"$set": lead_data},
        upsert=True
    )

async def mark_notified(post_id: str):
    db = get_db()
    await db.leads.update_one(
        {"post_id": post_id},
        {"$set": {"notified": True}}
    )

async def log_scan(new_posts: int, leads_found: int, duration: float):
    db = get_db()
    await db.scan_logs.insert_one({
        "new_posts": new_posts,
        "leads_found": leads_found,
        "duration_sec": duration,
        "run_at": datetime.now(timezone.utc)
    })

async def save_ai_log(post_id: str, input_prompt: str, output_response: str, tokens: int = 0):
    db = get_db()
    await db.ai_logs.insert_one({
        "post_id": post_id,
        "input_prompt": input_prompt,
        "output_response": output_response,
        "tokens_used": tokens,
        "created_at": datetime.now(timezone.utc)
    })
