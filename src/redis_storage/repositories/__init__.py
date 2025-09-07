from typing import Optional

from src.redis_storage import redis


class RedisRepo:
    def __init__(
        self, prefix: str, key: Optional[str] = None, ttl: Optional[int] = None
    ) -> None:
        self.prefix = prefix
        self.default_key = key
        self.ttl = ttl
        self.redis = redis

    def _key(self, key: Optional[str] = None) -> str:
        raw_key = key or self.default_key or self.prefix
        return f"{self.prefix}:{raw_key}"

    async def set(self, value: str, key: Optional[str] = None):
        return await self.redis.set(self._key(key), value, ex=self.ttl)

    async def get(self, key: Optional[str] = None) -> Optional[bytes]:
        return await self.redis.get(self._key(key))

    async def h_set(self, data: Optional[dict] = None, key: Optional[str] = None):
        data = data or {}
        real_key = self._key(key)
        await self.redis.hset(real_key, mapping=data)
        if self.ttl:
            await self.redis.expire(real_key, self.ttl)

    async def h_get(self, field: str, key: Optional[str] = None) -> Optional[bytes]:
        return await self.redis.hget(self._key(key), field)

    async def h_get_all(self, key: Optional[str] = None) -> dict[bytes, bytes]:
        return await self.redis.hgetall(self._key(key))

    async def delete(self, key: Optional[str] = None):
        return await self.redis.delete(self._key(key))
