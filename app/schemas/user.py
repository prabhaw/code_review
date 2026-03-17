import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, examples=["John Doe"])
    email: EmailStr = Field(..., examples=["john@example.com"])


class UserUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    email: EmailStr | None = None
    is_active: bool | None = None


class UserRead(BaseModel):
    id: uuid.UUID
    name: str
    email: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
