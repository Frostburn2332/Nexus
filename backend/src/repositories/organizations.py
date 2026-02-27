import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Organization


class OrganizationRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, name: str) -> Organization:
        org = Organization(name=name)
        self.db.add(org)
        await self.db.flush()
        return org

    async def get_by_id(self, org_id: uuid.UUID) -> Organization | None:
        return await self.db.get(Organization, org_id)

    async def get_all(self) -> list[Organization]:
        result = await self.db.execute(select(Organization))
        return list(result.scalars().all())
