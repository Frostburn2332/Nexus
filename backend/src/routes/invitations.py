import uuid
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.db import get_db
from src.models import User, UserRole, InvitationStatus
from src.auth.dependencies import require_role
from src.services import InvitationService
from src.services.email import get_email_provider
from src.repositories import InvitationRepository, OrganizationRepository

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


class InvitationPreviewResponse(BaseModel):
    """Public preview returned before the invitee starts OAuth.
    Intentionally omits the token and internal IDs."""
    invitee_name: str
    invitee_email: str
    organization_name: str
    role: str
    expires_at: datetime


@router.get("/preview/{token}", response_model=InvitationPreviewResponse)
async def preview_invitation(
    token: str,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Public endpoint — no auth required.
    Lets the frontend show 'You've been invited to join Acme Corp' before
    the invitee is redirected to Google OAuth."""
    invitation_repo = InvitationRepository(db)
    invitation = await invitation_repo.get_by_token(token)

    if invitation is None or invitation.status != InvitationStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found or no longer valid",
        )

    if invitation.expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Invitation has expired",
        )

    org_repo = OrganizationRepository(db)
    org = await org_repo.get_by_id(invitation.organization_id)

    return InvitationPreviewResponse(
        invitee_name=invitation.name,
        invitee_email=invitation.email,
        organization_name=org.name if org else "your organization",
        role=invitation.role.value,
        expires_at=invitation.expires_at,
    )


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
