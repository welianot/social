from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["auth"])

# Auth is handled by Supabase on the frontend.
# These endpoints are for server-side operations if needed later.


@router.get("/health")
async def auth_health():
    return {"status": "auth via supabase"}
