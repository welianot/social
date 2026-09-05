import time
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from cache.redis_client import get_redis

RATE_LIMIT = 100  # requests per window
WINDOW_SECONDS = 60


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in ("/health", "/docs", "/openapi.json"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        key = f"rl:{client_ip}"

        try:
            redis = await get_redis()
            current = await redis.incr(key)
            if current == 1:
                await redis.expire(key, WINDOW_SECONDS)
            if current > RATE_LIMIT:
                raise HTTPException(
                    status.HTTP_429_TOO_MANY_REQUESTS,
                    "Rate limit exceeded. Try again later.",
                )
        except HTTPException:
            raise
        except Exception:
            pass  # Redis unavailable — allow request through

        return await call_next(request)
