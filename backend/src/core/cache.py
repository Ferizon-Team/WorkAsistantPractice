from contextlib import asynccontextmanager
from typing import AsyncGenerator

from redis.asyncio import Redis as AsyncRedis

from src.core.config import settings


@asynccontextmanager
async def get_redis_client() -> AsyncGenerator[AsyncRedis, None]:
	async with AsyncRedis(
			host=settings.REDIS_HOST,
			port=settings.REDIS_PORT,
			db=settings.REDIS_DB) as redis:

		yield redis