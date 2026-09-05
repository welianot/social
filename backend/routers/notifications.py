from fastapi import APIRouter, Depends
from core.deps import get_current_user
from core.database import supabase

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("")
async def list_notifications(
    page: int = 1, page_size: int = 20, user: dict = Depends(get_current_user)
):
    offset = (page - 1) * page_size
    result = (
        supabase.table("notifications")
        .select("*")
        .eq("user_id", user["id"])
        .order("created_at", desc=True)
        .range(offset, offset + page_size - 1)
        .execute()
    )
    return {"items": result.data or [], "page": page}


@router.patch("/{notification_id}/read")
async def mark_read(notification_id: str, user: dict = Depends(get_current_user)):
    supabase.table("notifications").update({"read_at": "now()"}).eq(
        "id", notification_id
    ).eq("user_id", user["id"]).execute()
    return {"read": True}
