import math
from datetime import datetime, timezone
from uuid import UUID
import bcrypt
from beanie import SortDirection
from fastapi import APIRouter, HTTPException, Query

from app.i18n import t
from app.models import User
from app.schemas import UserCreate, UserRead, UserUpdate
from app.types import APIResponse, PaginatedResponse, SortOrder
from app.utils.valkey import cache_get, cache_set, cache_delete

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("register", response_model=APIResponse[UserRead], status_code=201)
async def create_user(
    body: UserCreate,
) -> APIResponse[UserRead]:
    existing = await User.find_one(User.email == body.email)
    if existing:
        raise HTTPException(status_code=409, detail=t("user.already_exists"))

    user = User(**body.model_dump())
    user.passowd = bcrypt.hashpw(user.password, bcrypt.gensalt(14))

    await user.insert()

    return APIResponse(
        success=True,
        message=t("user.created"),
        data=UserRead.model_validate(user),
    )


@router.get("", response_model=PaginatedResponse[UserRead])
async def list_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    sort: SortOrder = SortOrder.DESC,
    name: str | None = Query(None, description="Filter by name (case-insensitive partial match)"),
    email: str | None = Query(None, description="Filter by email (case-insensitive partial match)"),
    is_active: bool | None = Query(None, description="Filter by active status"),
) -> PaginatedResponse[UserRead]:
    cache_key = f"users:list:{page}:{limit}:{sort.value}:{name}:{email}:{is_active}"
    cached = await cache_get(cache_key)
    if cached:
        return PaginatedResponse(**cached)

    sort_dir = SortDirection.DESCENDING if sort == SortOrder.DESC else SortDirection.ASCENDING

    filters: dict = {}
    if name is not None:
        filters["name"] = {"$regex": name, "$options": "i"}
    if email is not None:
        filters["email"] = {"$regex": email, "$options": "i"}
    if is_active is not None:
        filters["is_active"] = is_active

    query = User.find(filters)
    total = await User.find(filters).count()

    users = (
        await query
        .sort((User.created_at, sort_dir))
        .skip((page - 1) * limit)
        .limit(limit)
        .to_list()
    )

    response = PaginatedResponse(
        items=[UserRead.model_validate(u) for u in users],
        total=total,
        page=page,
        limit=limit,
        pages=math.ceil(total / limit) if total > 0 else 0,
    )

    await cache_set(cache_key, response.model_dump(mode="json"), ttl=60)
    return response


@router.get("/{user_id}", response_model=APIResponse[UserRead])
async def get_user(
    user_id: UUID,
) -> APIResponse[UserRead]:
    cache_key = f"users:{user_id}"
    cached = await cache_get(cache_key)
    if cached:
        return APIResponse(success=True, message=t("success"), data=UserRead(**cached))

    user = await User.find_one(User.id == user_id)
    if not user:
        raise HTTPException(status_code=404, detail=t("user.not_found"))

    user_data = UserRead.model_validate(user)
    await cache_set(cache_key, user_data.model_dump(mode="json"), ttl=120)

    return APIResponse(success=True, message=t("success"), data=user_data)


@router.patch("/{user_id}", response_model=APIResponse[UserRead])
async def update_user(
    user_id: UUID,
    body: UserUpdate,
) -> APIResponse[UserRead]:
    user = await User.find_one(User.id == user_id)
    if not user:
        raise HTTPException(status_code=404, detail=t("user.not_found"))

    update_data = body.model_dump(exclude_unset=True)
    if update_data:
        update_data["updated_at"] = datetime.now(timezone.utc)
        await user.set(update_data)

    return APIResponse(
        success=True,
        message=t("user.updated"),
        data=UserRead.model_validate(user),
    )


@router.delete("/{user_id}", response_model=APIResponse[None])
async def delete_user(
    user_id: UUID,
) -> APIResponse[None]:
    user = await User.find_one(User.id == user_id)
    if not user:
        raise HTTPException(status_code=404, detail=t("user.not_found"))

    await user.delete()

    await cache_delete(f"users:{user_id}")

    return APIResponse(success=True, message=t("user.deleted"), data=None)
