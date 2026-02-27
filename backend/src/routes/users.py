import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_db
from src.models import User, UserRole
from src.auth.dependencies import get_current_user, require_role
from src.services import UserService

router = APIRouter(prefix="/users", tags=["users"])


class UserResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    email: str
    name: str
    profile_picture: str | None
    role: str
    status: str

    model_config = {"from_attributes": True}


class UpdateRoleRequest(BaseModel):
    role: UserRole


@router.get("", response_model=list[UserResponse])
async def list_users(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    user_service = UserService(db)
    return await user_service.list_by_organization(current_user.organization_id)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user


@router.patch("/{user_id}/role", response_model=UserResponse)
async def update_user_role(
    user_id: uuid.UUID,
    body: UpdateRoleRequest,
    current_user: Annotated[User, Depends(require_role(UserRole.MANAGER))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    user_service = UserService(db)
    return await user_service.update_role(user_id, body.role, current_user)


@router.delete("/{user_id}", status_code=204)
async def delete_user(
    user_id: uuid.UUID,
    current_user: Annotated[User, Depends(require_role(UserRole.ADMIN))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    user_service = UserService(db)
    await user_service.delete_user(user_id, current_user)
