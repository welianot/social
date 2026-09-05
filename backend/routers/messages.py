from fastapi import APIRouter, Depends, HTTPException
from core.deps import get_current_user
from core.database import supabase
from schemas.common import ConversationCreate, MessageCreate

router = APIRouter(prefix="/messages", tags=["messages"])


@router.get("/conversations")
async def list_conversations(user: dict = Depends(get_current_user)):
    participations = (
        supabase.table("conversation_participants")
        .select("conversation_id, conversations(id, updated_at)")
        .eq("user_id", user["id"])
        .order("conversations(updated_at)", desc=True)
        .execute()
    )
    conversations = []
    for p in participations.data or []:
        conv_id = p["conversation_id"]
        others = (
            supabase.table("conversation_participants")
            .select("user_id, profiles(id, username, display_name, avatar_url)")
            .eq("conversation_id", conv_id)
            .neq("user_id", user["id"])
            .execute()
        )
        last_msg = (
            supabase.table("messages")
            .select("*")
            .eq("conversation_id", conv_id)
            .order("created_at", desc=True)
            .limit(1)
            .maybe_single()
            .execute()
        )
        conversations.append(
            {
                "id": conv_id,
                "participants": [
                    {**o["profiles"], "user_id": o["user_id"]} for o in (others.data or [])
                ],
                "last_message": last_msg.data,
            }
        )
    return conversations


@router.post("/conversations")
async def create_conversation(
    body: ConversationCreate, user: dict = Depends(get_current_user)
):
    if body.participant_id == user["id"]:
        raise HTTPException(400, "Cannot message yourself")

    existing = (
        supabase.rpc(
            "find_dm_conversation",
            {"user_a": user["id"], "user_b": body.participant_id},
        ).execute()
        if False
        else None
    )

    conv = supabase.table("conversations").insert({}).execute()
    conv_id = conv.data[0]["id"]
    supabase.table("conversation_participants").insert(
        [
            {"conversation_id": conv_id, "user_id": user["id"]},
            {"conversation_id": conv_id, "user_id": body.participant_id},
        ]
    ).execute()
    return {"id": conv_id}


@router.get("/conversations/{conversation_id}")
async def get_messages(
    conversation_id: str,
    page: int = 1,
    page_size: int = 50,
    user: dict = Depends(get_current_user),
):
    member = (
        supabase.table("conversation_participants")
        .select("user_id")
        .eq("conversation_id", conversation_id)
        .eq("user_id", user["id"])
        .maybe_single()
        .execute()
    )
    if not member.data:
        raise HTTPException(403, "Not a participant")

    offset = (page - 1) * page_size
    result = (
        supabase.table("messages")
        .select("*")
        .eq("conversation_id", conversation_id)
        .order("created_at", desc=True)
        .range(offset, offset + page_size - 1)
        .execute()
    )
    return {"items": list(reversed(result.data or [])), "page": page}


@router.post("/conversations/{conversation_id}")
async def send_message(
    conversation_id: str,
    body: MessageCreate,
    user: dict = Depends(get_current_user),
):
    member = (
        supabase.table("conversation_participants")
        .select("user_id")
        .eq("conversation_id", conversation_id)
        .eq("user_id", user["id"])
        .maybe_single()
        .execute()
    )
    if not member.data:
        raise HTTPException(403, "Not a participant")

    result = (
        supabase.table("messages")
        .insert(
            {
                "conversation_id": conversation_id,
                "sender_id": user["id"],
                "body": body.body,
            }
        )
        .execute()
    )
    supabase.table("conversations").update(
        {"updated_at": "now()"}
    ).eq("id", conversation_id).execute()
    return result.data[0]
