"""
arq worker entry point.

Run with: arq app.worker.WorkerSettings
"""

import logging
from typing import Any

from app.utils.queue import get_queue_settings

logger = logging.getLogger(__name__)


async def sample_task(ctx: dict[str, Any], name: str) -> str:
    """Example background task."""
    logger.info("Running sample_task for %s", name)
    return f"Hello, {name}!"


class WorkerSettings:
    """arq worker configuration backed by Valkey."""

    functions = [sample_task]
    redis_settings = get_queue_settings()
    max_jobs = 10
    job_timeout = 300
