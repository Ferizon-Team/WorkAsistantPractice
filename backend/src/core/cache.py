from contextlib import asynccontextmanager
from typing import AsyncGenerator

from redis.asyncio import Redis as AsyncRedis

from src.core.config import settings


async def get_redis_client() -> AsyncGenerator[AsyncRedis, None]:
	async with AsyncRedis(
			host=settings.cache.host,
			port=settings.cache.port,
			db=settings.cache.db) as redis:

		yield redis

def create_redis_client() -> AsyncRedis:
    return AsyncRedis(
        host=settings.cache.host,
        port=settings.cache.port,
        db=settings.cache.db,
    )