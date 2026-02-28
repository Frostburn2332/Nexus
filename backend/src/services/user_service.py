import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import User, UserRole, UserStatus
from src.repositories import UserRepository


class UserService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.user_repo = UserRepository(db)

    async def get_by_id(self, user_id: uuid.UUID) -> User:
        user = await self.user_repo.get_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user

    async def get_by_email(self, email: str) -> User | None:
        return await self.user_repo.get_by_email(email)

    async def list_by_organization(self, organization_id: uuid.UUID) -> list[User]:
        return await self.user_repo.get_by_organization(organization_id)

    async def update_role(
        self, user_id: uuid.UUID, new_role: UserRole, current_user: User
    ) -> User:
        target = await self.get_by_id(user_id)

        if target.id == current_user.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot change your own role")

        if current_user.role == UserRole.MANAGER:
            if target.role != UserRole.VIEWER:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Managers can only edit the role of Viewers",
                )
            if new_role == UserRole.ADMIN:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Managers cannot promote users to Admin",
                )

        return await self.user_repo.update_role(target, new_role)

    async def delete_user(self, user_id: uuid.UUID, current_user: User) -> None:
        target = await self.get_by_id(user_id)

        if target.id == current_user.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete yourself")

        await self.user_repo.delete(target)

    async def activate_user(
        self, user: User, name: str | None = None, profile_picture: str | None = None
    ) -> User:
        await self.user_repo.update_status(user, UserStatus.ACTIVE)
        if name or profile_picture:
            await self.user_repo.update_profile(user, name=name, profile_picture=profile_picture)
        return user
