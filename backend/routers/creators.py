from fastapi import APIRouter, Depends
from core.deps import get_current_user

router = APIRouter(prefix="/creators", tags=["creators"])

# Phase 2: Creator tiers, subscriptions, stats


@router.post("/enable")
async def enable_creator(user: dict = Depends(get_current_user)):
    from core.database import supabase

    supabase.table("profiles").update({"is_creator": True}).eq(
        "id", user["id"]
    ).execute()
    return {"is_creator": True}


@router.get("/status")
async def creators_status():
    return {"phase": 2, "status": "partial — enable_creator ready"}
