import redis.asyncio as redis
from app.config import settings

CACHE_TTL = 120  # 2 * 60 minutes


class RedisCache:

    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.redis = None

    async def connect(self):
        self.redis = await redis.from_url(self.redis_url, decode_responses=True)

    async def _ensure_connected(self):
        if self.redis is None:
            await self.connect()

    async def get(self, key: str):
        await self._ensure_connected()
        return await self.redis.get(key)

    async def set(self, key: str, value: str, ttl: int = CACHE_TTL):
        await self._ensure_connected()
        await self.redis.set(key, value, ex=ttl)


redis_cache = RedisCache(settings.redis_url)
