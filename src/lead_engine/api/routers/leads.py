from fastapi import APIRouter, HTTPException, Query, status, BackgroundTasks
from lead_engine.api.schemas.leads import LeadListResponse, LeadMutationResponse, UpdateLeadRequest, LeadSchema
from lead_engine.engine import run_scan
from lead_engine.database import get_db
from datetime import datetime, timezone

router = APIRouter(prefix="/leads", tags=["leads"])

@router.get("", response_model=LeadListResponse)
async def list_leads(
    *,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=500),
    min_score: int = Query(default=70),
) -> LeadListResponse:
    offset = (page - 1) * page_size
    db = get_db()
    
    query = {"score": {"$gte": min_score}}
    
    total = await db.leads.count_documents(query)
    
    # Sort by score descending first, then by discovery date
    cursor = db.leads.find(query).sort([("score", -1), ("found_at", -1)]).skip(offset).limit(page_size)
    rows = await cursor.to_list(length=page_size)
    
    # MongoDB _id is not in LeadSchema, we use post_id as primary ref or map _id if needed
    # But for now we just need the fields in LeadSchema
    items = []
    for row in rows:
        # Use post_id as the unique id for the frontend
        row["id"] = row["post_id"]
        items.append(LeadSchema(**row))
    
    return LeadListResponse(items=items, total=total, page=page, page_size=page_size)

@router.get("/{post_id}", response_model=LeadSchema)
async def get_lead(post_id: str):
    db = get_db()
    row = await db.leads.find_one({"post_id": post_id})
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="lead not found")
    row["id"] = row["post_id"]
    return LeadSchema(**row)

@router.patch("/{post_id}", response_model=LeadMutationResponse)
async def patch_lead(
    post_id: str,
    payload: UpdateLeadRequest,
) -> LeadMutationResponse:
    db = get_db()
    if payload.status:
        await db.leads.update_one(
            {"post_id": post_id},
            {"$set": {"status": payload.status, "updated_at": datetime.now(timezone.utc)}}
        )
    return LeadMutationResponse(id=post_id)

@router.post("/scan")
async def trigger_scan(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_scan)
    return {"status": "scan_started", "message": "The Reddit scan has been triggered in the background."}
