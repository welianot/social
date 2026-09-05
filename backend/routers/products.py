from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, HttpUrl
from core.deps import get_current_user
from core.database import supabase
from core.config import settings
from services.affiliate import fetch_affiliate_product, inject_affiliate_tag

router = APIRouter(prefix="/products", tags=["products"])

# Phase 3: Marketplace + affiliate links


class AffiliateLinkCreate(BaseModel):
    url: HttpUrl


@router.post("/affiliate/preview")
async def preview_affiliate_link(body: AffiliateLinkCreate):
    """Paste Amazon/Flipkart link → auto-fetch title, image, price."""
    tagged_url = inject_affiliate_tag(
        str(body.url), settings.amazon_affiliate_tag, settings.flipkart_affiliate_id
    )
    product = await fetch_affiliate_product(tagged_url)
    return product


@router.post("/affiliate")
async def create_affiliate_listing(
    body: AffiliateLinkCreate, user: dict = Depends(get_current_user)
):
    tagged_url = inject_affiliate_tag(
        str(body.url), settings.amazon_affiliate_tag, settings.flipkart_affiliate_id
    )
    product = await fetch_affiliate_product(tagged_url)
    result = (
        supabase.table("products")
        .insert(
            {
                "seller_id": user["id"],
                "title": product["title"] or "Untitled Product",
                "image_url": product.get("image_url"),
                "price_cents": product.get("price_cents"),
                "is_affiliate": True,
                "affiliate_url": tagged_url,
                "affiliate_source": product["affiliate_source"],
                "affiliate_meta": product.get("affiliate_meta", {}),
            }
        )
        .execute()
    )
    return result.data[0]


@router.get("/status")
async def products_status():
    return {"phase": 3, "status": "affiliate preview ready"}
