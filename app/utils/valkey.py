import json
from typing import Any

import valkey.asyncio as valkey

from app.config import settings

_pool: valkey.ConnectionPool | None = None


async def get_valkey_pool() -> valkey.ConnectionPool:
    global _pool
    if _pool is None:
        _pool = valkey.ConnectionPool(
            host=settings.VALKEY_HOST,
            port=settings.VALKEY_PORT,
            db=settings.VALKEY_DB,
            password=settings.VALKEY_PASSWORD,
            decode_responses=True,
        )
    return _pool


async def get_valkey() -> valkey.Valkey:
    pool = await get_valkey_pool()
    return valkey.Valkey(connection_pool=pool)


async def cache_set(key: str, value: Any, ttl: int = 300) -> None:
    """Set a value in Valkey cache with TTL in seconds."""
    client = await get_valkey()
    await client.set(key, json.dumps(value), ex=ttl)


async def cache_get(key: str) -> Any | None:
    """Get a value from Valkey cache."""
    client = await get_valkey()
    data = await client.get(key)
    if data is None:
        return None
    return json.loads(data)


async def cache_delete(key: str) -> None:
    """Delete a key from Valkey cache."""
    client = await get_valkey()
    await client.delete(key)


async def close_valkey() -> None:
    global _pool
    if _pool is not None:
        await _pool.disconnect()
        _pool = None
