from fastapi import APIRouter, Depends
from core.deps import get_current_user, get_optional_user
from core.database import supabase
from schemas.common import PostResponse, PaginatedResponse
from routers.posts import _enrich_post

router = APIRouter(prefix="/feed", tags=["feed"])


@router.get("/home")
async def home_feed(
    page: int = 1,
    page_size: int = 20,
    user: dict = Depends(get_current_user),
):
    """Feed from people you follow + your own posts."""
    following = (
        supabase.table("follows")
        .select("following_id")
        .eq("follower_id", user["id"])
        .execute()
    )
    ids = [f["following_id"] for f in (following.data or [])]
    ids.append(user["id"])

    offset = (page - 1) * page_size
    result = (
        supabase.table("posts")
        .select("*", count="exact")
        .in_("creator_id", ids)
        .eq("is_adult", False)
        .order("created_at", desc=True)
        .range(offset, offset + page_size - 1)
        .execute()
    )
    posts = [_enrich_post(p, user["id"]) for p in (result.data or [])]
    total = result.count or 0
    return PaginatedResponse(
        items=posts,
        total=total,
        page=page,
        page_size=page_size,
        has_more=offset + page_size < total,
    )


@router.get("/trending")
async def trending_feed(
    page: int = 1,
    page_size: int = 20,
    user: dict | None = Depends(get_optional_user),
):
    offset = (page - 1) * page_size
    result = (
        supabase.table("posts")
        .select("*", count="exact")
        .eq("is_adult", False)
        .order("like_count", desc=True)
        .range(offset, offset + page_size - 1)
        .execute()
    )
    uid = user["id"] if user else None
    posts = [_enrich_post(p, uid) for p in (result.data or [])]
    total = result.count or 0
    return PaginatedResponse(
        items=posts,
        total=total,
        page=page,
        page_size=page_size,
        has_more=offset + page_size < total,
    )


@router.get("/user/{username}")
async def user_feed(
    username: str,
    page: int = 1,
    page_size: int = 20,
    user: dict | None = Depends(get_optional_user),
):
    profile = (
        supabase.table("profiles")
        .select("id")
        .eq("username", username)
        .maybe_single()
        .execute()
    )
    if not profile.data:
        return PaginatedResponse(items=[], total=0, page=page, page_size=page_size, has_more=False)

    offset = (page - 1) * page_size
    result = (
        supabase.table("posts")
        .select("*", count="exact")
        .eq("creator_id", profile.data["id"])
        .eq("is_adult", False)
        .order("created_at", desc=True)
        .range(offset, offset + page_size - 1)
        .execute()
    )
    uid = user["id"] if user else None
    posts = [_enrich_post(p, uid) for p in (result.data or [])]
    total = result.count or 0
    return PaginatedResponse(
        items=posts,
        total=total,
        page=page,
        page_size=page_size,
        has_more=offset + page_size < total,
    )
