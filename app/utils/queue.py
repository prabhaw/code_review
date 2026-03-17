"""
Task queue using arq (async job queue backed by Valkey/Redis).

Usage:
    from app.utils.queue import enqueue

    await enqueue("send_email", to="user@example.com", subject="Hello")
"""

from typing import Any

from arq import create_pool
from arq.connections import RedisSettings, ArqRedis

from app.config import settings

_pool: ArqRedis | None = None


def get_queue_settings() -> RedisSettings:
    return RedisSettings(
        host=settings.VALKEY_HOST,
        port=settings.VALKEY_PORT,
        database=settings.VALKEY_DB,
        password=settings.VALKEY_PASSWORD,
    )


async def get_queue_pool() -> ArqRedis:
    global _pool
    if _pool is None:
        _pool = await create_pool(get_queue_settings())
    return _pool


async def enqueue(task_name: str, **kwargs: Any) -> Any:
    """Enqueue a background job."""
    pool = await get_queue_pool()
    return await pool.enqueue_job(task_name, **kwargs)


async def close_queue() -> None:
    global _pool
    if _pool is not None:
        await _pool.aclose()
        _pool = None
