import uuid

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import User, UserRole, UserStatus


class UserRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(
        self,
        organization_id: uuid.UUID,
        email: str,
        name: str,
        role: UserRole,
        status: UserStatus = UserStatus.PENDING,
        profile_picture: str | None = None,
    ) -> User:
        user = User(
            organization_id=organization_id,
            email=email,
            name=name,
            role=role,
            status=status,
            profile_picture=profile_picture,
        )
        self.db.add(user)
        await self.db.flush()
        return user

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        return await self.db.get(User, user_id)

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_email_and_org(
        self, email: str, organization_id: uuid.UUID
    ) -> User | None:
        result = await self.db.execute(
            select(User).where(
                and_(User.email == email, User.organization_id == organization_id)
            )
        )
        return result.scalar_one_or_none()

    async def get_by_organization(self, organization_id: uuid.UUID) -> list[User]:
        result = await self.db.execute(
            select(User).where(User.organization_id == organization_id)
        )
        return list(result.scalars().all())

    async def update_role(self, user: User, role: UserRole) -> User:
        user.role = role
        await self.db.flush()
        return user

    async def update_status(self, user: User, status: UserStatus) -> User:
        user.status = status
        await self.db.flush()
        return user

    async def update_profile(
        self, user: User, name: str | None = None, profile_picture: str | None = None
    ) -> User:
        if name is not None:
            user.name = name
        if profile_picture is not None:
            user.profile_picture = profile_picture
        await self.db.flush()
        return user

    async def delete(self, user: User) -> None:
        await self.db.delete(user)
        await self.db.flush()
