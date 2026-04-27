from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from lead_engine.api.scheduler_manager import scheduler_manager
from lead_engine.database import get_db

router = APIRouter(prefix="/scheduler", tags=["scheduler"])

class SchedulerConfig(BaseModel):
    interval_minutes: int

@router.get("/status")
async def get_status():
    return scheduler_manager.get_status()

@router.post("/start")
async def start_scheduler(config: SchedulerConfig):
    if config.interval_minutes < 1:
        raise HTTPException(status_code=400, detail="Interval must be at least 1 minute")
    scheduler_manager.start(config.interval_minutes)
    return {"status": "started", "config": config}

@router.post("/stop")
async def stop_scheduler():
    scheduler_manager.stop()
    return {"status": "stopped"}

@router.get("/logs")
async def get_logs(limit: int = 20):
    db = get_db()
    cursor = db.scan_logs.find().sort("run_at", -1).limit(limit)
    rows = await cursor.to_list(length=limit)
    # Convert MongoDB _id to string or remove it
    for row in rows:
        row["id"] = str(row["_id"])
        del row["_id"]
    return rows

# Add a cron endpoint for Vercel
@router.get("/cron")
async def vercel_cron_trigger():
    # This endpoint will be called by Vercel Cron
    await scheduler_manager.run_scan_once() # We might need to expose this
    return {"status": "success"}
