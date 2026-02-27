import secrets
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.models import Invitation, InvitationStatus, User, UserRole, UserStatus
from src.repositories import InvitationRepository, UserRepository


INVITATION_EXPIRY_DAYS = 7


class InvitationService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.invitation_repo = InvitationRepository(db)
        self.user_repo = UserRepository(db)

    async def create_invitation(
        self, organization_id: uuid.UUID, email: str, name: str, role: UserRole, invited_by: uuid.UUID
    ) -> Invitation:
        existing_user = await self.user_repo.get_by_email_and_org(email, organization_id)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists in the organization",
            )

        existing_invitation = await self.invitation_repo.get_pending_by_email_and_org(email, organization_id)
        if existing_invitation:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A pending invitation already exists for this email",
            )

        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(days=INVITATION_EXPIRY_DAYS)

        invitation = await self.invitation_repo.create(
            organization_id=organization_id,
            email=email,
            name=name,
            role=role,
            token=token,
            invited_by=invited_by,
            expires_at=expires_at,
        )

        invitation_link = f"{settings.frontend_url}/invite/accept?token={token}"
        print(f"\n{'='*60}")
        print(f"INVITATION LINK for {email}:")
        print(f"{invitation_link}")
        print(f"{'='*60}\n")

        return invitation

    async def get_by_token(self, token: str) -> Invitation:
        invitation = await self.invitation_repo.get_by_token(token)
        if invitation is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invitation not found")
        return invitation

    async def accept_invitation(self, token: str, oauth_email: str, oauth_name: str, profile_picture: str | None = None) -> User:
        invitation = await self.get_by_token(token)

        if invitation.status != InvitationStatus.PENDING:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invitation is no longer valid")

        if datetime.now(timezone.utc) > invitation.expires_at.replace(tzinfo=timezone.utc):
            await self.invitation_repo.update_status(invitation, InvitationStatus.EXPIRED)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invitation has expired")

        if oauth_email.lower() != invitation.email.lower():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="OAuth email does not match invitation email",
            )

        user = await self.user_repo.create(
            organization_id=invitation.organization_id,
            email=invitation.email,
            name=oauth_name or invitation.name,
            role=invitation.role,
            status=UserStatus.ACTIVE,
            profile_picture=profile_picture,
        )

        await self.invitation_repo.update_status(invitation, InvitationStatus.ACCEPTED)

        return user

    async def list_pending(self, organization_id: uuid.UUID) -> list[Invitation]:
        return await self.invitation_repo.get_pending_by_org(organization_id)
