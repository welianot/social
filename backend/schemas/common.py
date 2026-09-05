from pydantic import BaseModel, Field
from datetime import datetime
from typing import Any


class ProfileUpdate(BaseModel):
    display_name: str | None = None
    bio: str | None = None
    country: str | None = Field(None, max_length=2)
    language: str | None = Field(None, max_length=5)
    interests: list[str] | None = None
    avatar_url: str | None = None


class ProfileResponse(BaseModel):
    id: str
    username: str
    display_name: str | None
    bio: str | None
    avatar_url: str | None
    country: str | None
    language: str | None
    interests: list[str]
    is_creator: bool
    is_verified: bool
    follower_count: int
    following_count: int
    post_count: int
    created_at: datetime


class PostCreate(BaseModel):
    content_type: str = "photo"
    caption: str | None = None
    visibility: str = "public"
    is_adult: bool = False
    metadata: dict[str, Any] = {}


class PostResponse(BaseModel):
    id: str
    creator_id: str
    content_type: str
    caption: str | None
    visibility: str
    is_adult: bool
    metadata: dict[str, Any]
    like_count: int
    comment_count: int
    created_at: datetime
    media: list[dict] = []
    creator: ProfileResponse | None = None
    liked_by_me: bool = False


class CommentCreate(BaseModel):
    body: str = Field(..., min_length=1, max_length=2000)
    parent_id: str | None = None


class CommentResponse(BaseModel):
    id: str
    post_id: str
    user_id: str
    body: str
    parent_id: str | None
    created_at: datetime
    user: ProfileResponse | None = None


class MessageCreate(BaseModel):
    body: str = Field(..., min_length=1, max_length=5000)


class ConversationCreate(BaseModel):
    participant_id: str


class PaginatedResponse(BaseModel):
    items: list[Any]
    total: int
    page: int
    page_size: int
    has_more: bool
