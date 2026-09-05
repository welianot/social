from fastapi import APIRouter, Depends, HTTPException
from core.deps import get_current_user
from core.database import supabase
from schemas.common import ProfileUpdate, ProfileResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=ProfileResponse)
async def get_me(user: dict = Depends(get_current_user)):
    return user


@router.patch("/me", response_model=ProfileResponse)
async def update_me(body: ProfileUpdate, user: dict = Depends(get_current_user)):
    updates = body.model_dump(exclude_none=True)
    if not updates:
        return user
    result = (
        supabase.table("profiles")
        .update(updates)
        .eq("id", user["id"])
        .execute()
    )
    return result.data[0]


@router.get("/{username}", response_model=ProfileResponse)
async def get_profile(username: str):
    result = (
        supabase.table("profiles")
        .select("*")
        .eq("username", username)
        .maybe_single()
        .execute()
    )
    if not result.data:
        raise HTTPException(404, "User not found")
    return result.data


@router.post("/{username}/follow")
async def follow_user(username: str, user: dict = Depends(get_current_user)):
    target = (
        supabase.table("profiles")
        .select("id")
        .eq("username", username)
        .maybe_single()
        .execute()
    )
    if not target.data:
        raise HTTPException(404, "User not found")
    if target.data["id"] == user["id"]:
        raise HTTPException(400, "Cannot follow yourself")
    supabase.table("follows").upsert(
        {"follower_id": user["id"], "following_id": target.data["id"]}
    ).execute()
    return {"following": True}


@router.delete("/{username}/follow")
async def unfollow_user(username: str, user: dict = Depends(get_current_user)):
    target = (
        supabase.table("profiles")
        .select("id")
        .eq("username", username)
        .maybe_single()
        .execute()
    )
    if not target.data:
        raise HTTPException(404, "User not found")
    supabase.table("follows").delete().eq("follower_id", user["id"]).eq(
        "following_id", target.data["id"]
    ).execute()
    return {"following": False}


@router.get("/{username}/followers")
async def get_followers(username: str, page: int = 1, page_size: int = 20):
    profile = (
        supabase.table("profiles")
        .select("id")
        .eq("username", username)
        .maybe_single()
        .execute()
    )
    if not profile.data:
        raise HTTPException(404, "User not found")
    offset = (page - 1) * page_size
    result = (
        supabase.table("follows")
        .select("follower_id, profiles!follows_follower_id_fkey(*)")
        .eq("following_id", profile.data["id"])
        .range(offset, offset + page_size - 1)
        .execute()
    )
    return {"items": result.data, "page": page, "page_size": page_size}
