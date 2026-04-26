from collections.abc import AsyncIterator

import redis.asyncio as redis
from redis.asyncio import Redis

from src.config import get_settings


async def create_redis_client() -> Redis:
    settings = get_settings()
    return redis.from_url(settings.redis_url, decode_responses=True)


async def get_redis_client() -> AsyncIterator[Redis]:
    client = await create_redis_client()
    try:
        yield client
    finally:
        await client.aclose()

