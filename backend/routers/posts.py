from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from core.deps import get_current_user, get_optional_user
from core.database import supabase
from schemas.common import PostCreate, PostResponse, CommentCreate, CommentResponse
from services.media import upload_media
import json

router = APIRouter(prefix="/posts", tags=["posts"])


def _enrich_post(post: dict, user_id: str | None = None) -> dict:
    media = (
        supabase.table("post_media")
        .select("*")
        .eq("post_id", post["id"])
        .order("sort_order")
        .execute()
    )
    post["media"] = media.data or []

    creator = (
        supabase.table("profiles")
        .select("id, username, display_name, avatar_url, is_verified")
        .eq("id", post["creator_id"])
        .maybe_single()
        .execute()
    )
    post["creator"] = creator.data

    post["liked_by_me"] = False
    if user_id:
        like = (
            supabase.table("likes")
            .select("user_id")
            .eq("post_id", post["id"])
            .eq("user_id", user_id)
            .maybe_single()
            .execute()
        )
        post["liked_by_me"] = bool(like.data)
    return post


@router.post("", response_model=PostResponse)
async def create_post(
    content_type: str = Form("photo"),
    caption: str = Form(None),
    visibility: str = Form("public"),
    is_adult: bool = Form(False),
    metadata: str = Form("{}"),
    files: list[UploadFile] = File(default=[]),
    user: dict = Depends(get_current_user),
):
    meta = json.loads(metadata) if metadata else {}
    result = (
        supabase.table("posts")
        .insert(
            {
                "creator_id": user["id"],
                "content_type": content_type,
                "caption": caption,
                "visibility": visibility,
                "is_adult": is_adult,
                "metadata": meta,
            }
        )
        .execute()
    )
    post = result.data[0]

    bucket = "adult" if is_adult else "posts"
    for i, file in enumerate(files):
        media_data = await upload_media(file, user["id"], bucket=bucket)
        supabase.table("post_media").insert(
            {
                "post_id": post["id"],
                "url": media_data["url"],
                "media_type": media_data["media_type"],
                "sort_order": i,
            }
        ).execute()

    return _enrich_post(post, user["id"])


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: str, user: dict | None = Depends(get_optional_user)):
    result = (
        supabase.table("posts")
        .select("*")
        .eq("id", post_id)
        .maybe_single()
        .execute()
    )
    if not result.data:
        raise HTTPException(404, "Post not found")
    return _enrich_post(result.data, user["id"] if user else None)


@router.delete("/{post_id}")
async def delete_post(post_id: str, user: dict = Depends(get_current_user)):
    post = (
        supabase.table("posts")
        .select("creator_id")
        .eq("id", post_id)
        .maybe_single()
        .execute()
    )
    if not post.data:
        raise HTTPException(404, "Post not found")
    if post.data["creator_id"] != user["id"]:
        raise HTTPException(403, "Not your post")
    supabase.table("posts").delete().eq("id", post_id).execute()
    return {"deleted": True}


@router.post("/{post_id}/like")
async def like_post(post_id: str, user: dict = Depends(get_current_user)):
    supabase.table("likes").upsert(
        {"user_id": user["id"], "post_id": post_id}
    ).execute()
    return {"liked": True}


@router.delete("/{post_id}/like")
async def unlike_post(post_id: str, user: dict = Depends(get_current_user)):
    supabase.table("likes").delete().eq("user_id", user["id"]).eq(
        "post_id", post_id
    ).execute()
    return {"liked": False}


@router.get("/{post_id}/comments", response_model=list[CommentResponse])
async def get_comments(post_id: str, page: int = 1, page_size: int = 20):
    offset = (page - 1) * page_size
    result = (
        supabase.table("comments")
        .select("*, profiles(id, username, display_name, avatar_url)")
        .eq("post_id", post_id)
        .order("created_at")
        .range(offset, offset + page_size - 1)
        .execute()
    )
    comments = []
    for c in result.data or []:
        c["user"] = c.pop("profiles", None)
        comments.append(c)
    return comments


@router.post("/{post_id}/comments", response_model=CommentResponse)
async def add_comment(
    post_id: str, body: CommentCreate, user: dict = Depends(get_current_user)
):
    result = (
        supabase.table("comments")
        .insert(
            {
                "post_id": post_id,
                "user_id": user["id"],
                "body": body.body,
                "parent_id": body.parent_id,
            }
        )
        .execute()
    )
    comment = result.data[0]
    comment["user"] = {
        "id": user["id"],
        "username": user["username"],
        "display_name": user.get("display_name"),
        "avatar_url": user.get("avatar_url"),
    }
    return comment
