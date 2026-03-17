import uuid
from datetime import datetime, timezone

from beanie import Document, Indexed
from pydantic import Field


class User(Document):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    name: Indexed(str)  # type: ignore[valid-type]
    users: list[uuid.UUID] = Field(default_factory=list)
    description: str = Field(default="")
    repo_token: str = Field(default="")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "projects"
