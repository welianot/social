from jose import jwt, JWTError
from core.config import settings


def decode_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            audience="authenticated",
        )
        return payload
    except JWTError:
        return None
