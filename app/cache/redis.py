import redis.asyncio as redis
from app.config import settings

CACHE_TTL = 120  # Time-to-live for cache entries in seconds (2 minutes)


class RedisCache:
    """Asynchronous Redis cache handler."""

    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.redis: redis.Redis | None = None

    async def connect(self) -> None:
        """Establish a connection to Redis."""
        self.redis = await redis.from_url(self.redis_url, decode_responses=True)

    async def _ensure_connected(self) -> None:
        """Ensure Redis connection is established before any operation."""
        if self.redis is None:
            await self.connect()

    async def get(self, key: str) -> str | None:
        """Retrieve a value from Redis by key."""
        await self._ensure_connected()
        return await self.redis.get(key)

    async def set(self, key: str, value: str, ttl: int = CACHE_TTL) -> None:
        """Set a value in Redis with an optional TTL."""
        await self._ensure_connected()
        await self.redis.set(key, value, ex=ttl)


redis_cache = RedisCache(settings.redis_url)
