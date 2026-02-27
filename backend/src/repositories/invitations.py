import uuid
from datetime import datetime

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Invitation, InvitationStatus, UserRole


class InvitationRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(
        self,
        organization_id: uuid.UUID,
        email: str,
        name: str,
        role: UserRole,
        token: str,
        invited_by: uuid.UUID,
        expires_at: datetime,
    ) -> Invitation:
        invitation = Invitation(
            organization_id=organization_id,
            email=email,
            name=name,
            role=role,
            token=token,
            invited_by=invited_by,
            expires_at=expires_at,
        )
        self.db.add(invitation)
        await self.db.flush()
        return invitation

    async def get_by_token(self, token: str) -> Invitation | None:
        result = await self.db.execute(
            select(Invitation).where(Invitation.token == token)
        )
        return result.scalar_one_or_none()

    async def get_pending_by_org(self, organization_id: uuid.UUID) -> list[Invitation]:
        result = await self.db.execute(
            select(Invitation).where(
                and_(
                    Invitation.organization_id == organization_id,
                    Invitation.status == InvitationStatus.PENDING,
                )
            )
        )
        return list(result.scalars().all())

    async def get_pending_by_email_and_org(
        self, email: str, organization_id: uuid.UUID
    ) -> Invitation | None:
        result = await self.db.execute(
            select(Invitation).where(
                and_(
                    Invitation.email == email,
                    Invitation.organization_id == organization_id,
                    Invitation.status == InvitationStatus.PENDING,
                )
            )
        )
        return result.scalar_one_or_none()

    async def update_status(
        self, invitation: Invitation, status: InvitationStatus
    ) -> Invitation:
        invitation.status = status
        await self.db.flush()
        return invitation
