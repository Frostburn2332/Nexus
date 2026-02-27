import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.db import get_db
from src.models import User, UserRole
from src.auth.dependencies import require_role
from src.services import InvitationService
from src.services.email import get_email_provider

router = APIRouter(prefix="/invitations", tags=["invitations"])


class CreateInvitationRequest(BaseModel):
    email: EmailStr
    name: str
    role: UserRole


class InvitationResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    email: str
    name: str
    role: str
    token: str
    status: str

    model_config = {"from_attributes": True}


@router.post("", response_model=InvitationResponse, status_code=201)
async def create_invitation(
    body: CreateInvitationRequest,
    current_user: Annotated[User, Depends(require_role(UserRole.MANAGER))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    email_provider = get_email_provider(settings.email_provider)
    invitation_service = InvitationService(db, email_provider)
    return await invitation_service.create_invitation(
        organization_id=current_user.organization_id,
        email=body.email,
        name=body.name,
        role=body.role,
        invited_by=current_user.id,
    )


@router.get("", response_model=list[InvitationResponse])
async def list_pending_invitations(
    current_user: Annotated[User, Depends(require_role(UserRole.MANAGER))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    email_provider = get_email_provider(settings.email_provider)
    invitation_service = InvitationService(db, email_provider)
    return await invitation_service.list_pending(current_user.organization_id)
