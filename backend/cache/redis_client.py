import redis.asyncio as aioredis
from core.config import settings

redis_client: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    global redis_client
    if redis_client is None:
        redis_client = aioredis.from_url(settings.redis_url, decode_responses=True)
    return redis_client


class CacheKeys:
    FEED = "feed:{user_id}:{page}"
    PROFILE = "profile:{username}"
    TRENDING = "trending:posts"

    @staticmethod
    def feed(user_id: str, page: int) -> str:
        return f"feed:{user_id}:{page}"

    @staticmethod
    def profile(username: str) -> str:
        return f"profile:{username}"
