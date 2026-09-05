from fastapi import APIRouter, Query
from core.database import supabase

router = APIRouter(prefix="/explore", tags=["explore"])


@router.get("/users")
async def explore_users(
    country: str | None = None,
    interest: str | None = None,
    q: str | None = None,
    page: int = 1,
    page_size: int = 20,
):
    offset = (page - 1) * page_size
    query = supabase.table("profiles").select(
        "id, username, display_name, avatar_url, country, language, interests, follower_count, is_verified",
        count="exact",
    )

    if country:
        query = query.eq("country", country.upper())
    if interest:
        query = query.contains("interests", [interest])
    if q:
        query = query.or_(f"username.ilike.%{q}%,display_name.ilike.%{q}%")

    result = query.order("follower_count", desc=True).range(
        offset, offset + page_size - 1
    ).execute()

    return {
        "items": result.data or [],
        "total": result.count or 0,
        "page": page,
        "page_size": page_size,
    }


@router.get("/countries")
async def list_countries():
    result = (
        supabase.table("profiles")
        .select("country")
        .not_.is_("country", "null")
        .execute()
    )
    countries = {}
    for row in result.data or []:
        c = row["country"]
        countries[c] = countries.get(c, 0) + 1
    return sorted(
        [{"code": k, "count": v} for k, v in countries.items()],
        key=lambda x: x["count"],
        reverse=True,
    )
