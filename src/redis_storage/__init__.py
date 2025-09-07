from redis.asyncio import Redis

from src.core.config.settings import settings


redis = Redis.from_url(settings.redis.connection_url(), decode_responses=True)
