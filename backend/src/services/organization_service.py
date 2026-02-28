import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Organization, User, UserRole, UserStatus
from src.repositories import OrganizationRepository, UserRepository


class OrganizationService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.org_repo = OrganizationRepository(db)
        self.user_repo = UserRepository(db)

    async def register(
        self, org_name: str, admin_email: str, admin_name: str, profile_picture: str | None = None
    ) -> tuple[Organization, User]:
        """Create a new organization and its founding admin user."""
        org = await self.org_repo.create(name=org_name)

        admin = await self.user_repo.create(
            organization_id=org.id,
            email=admin_email,
            name=admin_name,
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
            profile_picture=profile_picture,
        )

        return org, admin

    async def get_by_id(self, org_id: uuid.UUID) -> Organization | None:
        return await self.org_repo.get_by_id(org_id)

    async def delete(self, org_id: uuid.UUID) -> None:
        """Delete an organization and all its data (cascade handled by DB)."""
        org = await self.org_repo.get_by_id(org_id)
        if org:
            await self.db.delete(org)
            await self.db.flush()
