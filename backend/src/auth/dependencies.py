import uuid
from typing import Annotated

import jwt as pyjwt
from fastapi import Depends, HTTPException, Path, status, Cookie
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_db
from src.models import User, UserRole
from src.repositories import UserRepository
from src.auth.jwt import verify_access_token
from src.auth.rbac import has_minimum_role

bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    try:
        payload = verify_access_token(credentials.credentials)
    except pyjwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user_id = uuid.UUID(payload["sub"])
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user


async def get_org_user(
    user_id: Annotated[uuid.UUID, Path()],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Resolves a {user_id} path parameter and asserts it belongs to the
    caller's organization. Prevents horizontal privilege escalation across
    tenant boundaries before the service layer is ever reached."""
    user_repo = UserRepository(db)
    target = await user_repo.get_by_id(user_id)

    if target is None or target.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    return target


def require_role(minimum_role: UserRole):
    async def role_checker(
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        if not has_minimum_role(current_user.role, minimum_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user
    return role_checker
