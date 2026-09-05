from fastapi import APIRouter, Depends, HTTPException
from core.deps import get_current_user
from core.database import supabase

router = APIRouter(prefix="/admin", tags=["admin"])

# TODO: add proper admin role check via profiles.is_admin column


@router.get("/stats")
async def platform_stats(user: dict = Depends(get_current_user)):
    profiles = supabase.table("profiles").select("id", count="exact").execute()
    posts = supabase.table("posts").select("id", count="exact").execute()
    return {
        "users": profiles.count or 0,
        "posts": posts.count or 0,
    }


@router.post("/ban/{user_id}")
async def ban_user(user_id: str, user: dict = Depends(get_current_user)):
    raise HTTPException(501, "Admin ban not yet implemented — add is_admin role")
