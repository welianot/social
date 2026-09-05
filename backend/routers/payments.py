from fastapi import APIRouter

router = APIRouter(prefix="/payments", tags=["payments"])

# Phase 2: Stripe + Razorpay integration


@router.get("/status")
async def payments_status():
    return {"phase": 2, "status": "not_implemented"}
