from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
import redis.asyncio as redis
from httpx import ASGITransport, AsyncClient
from redis.exceptions import RedisError

from src.config import get_settings
from src.main import app, get_notes_service
from src.services.notes_service import NotesService
from src.storage.redis_client import get_redis_client


class FakeRedis:
    def __init__(self):
        self.values: dict[str, str] = {}
        self.sets: dict[str, set[str]] = {}
        self.expires: dict[str, int] = {}

    async def set(self, key: str, value: str, ex: int | None = None):
        self.values[key] = value
        if ex is not None:
            self.expires[key] = ex
        else:
            self.expires.pop(key, None)
        return True

    async def get(self, key: str):
        return self.values.get(key)

    async def sadd(self, key: str, value: str):
        self.sets.setdefault(key, set()).add(value)
        return 1

    async def smembers(self, key: str):
        return set(self.sets.get(key, set()))

    async def srem(self, key: str, value: str):
        self.sets.setdefault(key, set()).discard(value)
        return 1

    async def incr(self, key: str):
        current_value = int(self.values.get(key, 0)) + 1
        self.values[key] = str(current_value)
        return current_value

    async def delete(self, key: str):
        existed = key in self.values
        self.values.pop(key, None)
        self.expires.pop(key, None)
        return int(existed)

    async def scan_iter(self, match: str):
        prefix = match.rstrip("*")
        for key in list(self.values):
            if key.startswith(prefix):
                yield key

    async def ttl(self, key: str):
        return self.expires.get(key, -1 if key in self.values else -2)

    async def ping(self):
        return True


@pytest.fixture
def fake_redis() -> FakeRedis:
    return FakeRedis()


@pytest.fixture
def notes_service(fake_redis: FakeRedis) -> NotesService:
    return NotesService(fake_redis)


@pytest_asyncio.fixture
async def api_client(fake_redis: FakeRedis) -> AsyncIterator[AsyncClient]:
    def override_service() -> NotesService:
        return NotesService(fake_redis)

    async def override_redis_client() -> AsyncIterator[FakeRedis]:
        yield fake_redis

    app.dependency_overrides[get_notes_service] = override_service
    app.dependency_overrides[get_redis_client] = override_redis_client
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def real_redis_client() -> AsyncIterator[redis.Redis]:
    client = redis.from_url(get_settings().redis_url, decode_responses=True)
    try:
        await client.ping()
    except RedisError:
        await client.aclose()
        pytest.skip("Redis is not available for integration tests")

    await client.flushdb()
    try:
        yield client
    finally:
        await client.flushdb()
        await client.aclose()
