from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from redis.asyncio import Redis

from .config import REDIS_URL


redis: Redis | None = None


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    global redis
    redis = Redis.from_url(REDIS_URL, decode_responses=True)
    yield
    if redis is not None:
        await redis.aclose()


def link_cache_key(short_code: str) -> str:
    return f"link:{short_code}"


async def get_link_cache(short_code: str) -> str | None:
    if redis is None:
        return None
    return await redis.get(link_cache_key(short_code))


async def set_link_cache(short_code: str, url: str, ttl: int = 3600) -> None:
    if redis is None:
        return
    await redis.set(link_cache_key(short_code), url, ex=ttl)


async def delete_link_cache(short_code: str) -> None:
    if redis is None:
        return
    await redis.delete(link_cache_key(short_code))
