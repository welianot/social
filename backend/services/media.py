import uuid
from fastapi import UploadFile, HTTPException
from core.database import supabase

ALLOWED_IMAGE = {"image/jpeg", "image/png", "image/webp", "image/gif"}
ALLOWED_VIDEO = {"video/mp4", "video/webm", "video/quicktime"}
MAX_IMAGE_BYTES = 10 * 1024 * 1024   # 10 MB
MAX_VIDEO_BYTES = 50 * 1024 * 1024   # 50 MB


async def upload_media(
    file: UploadFile,
    user_id: str,
    bucket: str = "posts",
) -> dict:
    content_type = file.content_type or ""
    data = await file.read()

    if content_type in ALLOWED_IMAGE:
        if len(data) > MAX_IMAGE_BYTES:
            raise HTTPException(400, "Image too large (max 10MB)")
        media_type = "image"
    elif content_type in ALLOWED_VIDEO:
        if len(data) > MAX_VIDEO_BYTES:
            raise HTTPException(400, "Video too large (max 50MB)")
        media_type = "video"
    else:
        raise HTTPException(400, f"Unsupported file type: {content_type}")

    ext = file.filename.rsplit(".", 1)[-1] if file.filename else "bin"
    path = f"{user_id}/{uuid.uuid4()}.{ext}"

    supabase.storage.from_(bucket).upload(
        path, data, {"content-type": content_type}
    )
    public_url = supabase.storage.from_(bucket).get_public_url(path)

    return {"url": public_url, "media_type": media_type, "path": path}
