from enum import Enum
from typing import Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel

# Common type aliases
ID = UUID

T = TypeVar("T")


class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"


class Locale(str, Enum):
    EN = "en"
    NE = "ne"


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    limit: int
    pages: int


class APIResponse(BaseModel, Generic[T]):
    success: bool
    message: str
    data: T | None = None
