from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from app.config import settings
from app.models.user import User

client: AsyncIOMotorClient = None  # type: ignore[assignment]


async def init_db() -> None:
    """Initialize MongoDB connection and Beanie ODM."""
    global client
    client = AsyncIOMotorClient(settings.MONGO_URL)
    await init_beanie(
        database=client[settings.MONGO_DB],
        document_models=[User],
    )


async def close_db() -> None:
    """Close MongoDB connection."""
    global client
    if client:
        client.close()
