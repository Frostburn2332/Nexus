import uuid
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_db
from src.models import User, UserRole
from src.auth.dependencies import get_current_user, get_org_user, require_role
from src.services import UserService, OrganizationService

router = APIRouter(prefix="/users", tags=["users"])


class UserResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    email: str
    name: str
    profile_picture: str | None
    role: str
    status: str
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class MeResponse(UserResponse):
    organization_name: str | None = None


class UpdateRoleRequest(BaseModel):
    role: UserRole


@router.get("", response_model=list[UserResponse])
async def list_users(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    user_service = UserService(db)
    return await user_service.list_by_organization(current_user.organization_id)


@router.get("/me", response_model=MeResponse)
async def get_me(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    org_service = OrganizationService(db)
    org = await org_service.get_by_id(current_user.organization_id)
    data = MeResponse.model_validate(current_user)
    data.organization_name = org.name if org else None
    return data


@router.patch("/{user_id}/role", response_model=UserResponse)
async def update_user_role(
    body: UpdateRoleRequest,
    current_user: Annotated[User, Depends(require_role(UserRole.MANAGER))],
    target_user: Annotated[User, Depends(get_org_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    user_service = UserService(db)
    return await user_service.update_role(target_user.id, body.role, current_user)


@router.delete("/{user_id}", status_code=204)
async def delete_user(
    current_user: Annotated[User, Depends(require_role(UserRole.ADMIN))],
    target_user: Annotated[User, Depends(get_org_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    user_service = UserService(db)
    await user_service.delete_user(target_user.id, current_user)
