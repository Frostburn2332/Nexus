import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_db
from src.models import User, UserRole
from src.auth.dependencies import require_role
from src.services import OrganizationService

router = APIRouter(prefix="/organizations", tags=["organizations"])


class DeleteOrganizationRequest(BaseModel):
    confirmation: str


@router.delete("/me", status_code=204)
async def delete_my_organization(
    body: DeleteOrganizationRequest,
    current_user: Annotated[User, Depends(require_role(UserRole.ADMIN))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    org_service = OrganizationService(db)
    org = await org_service.get_by_id(current_user.organization_id)
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    expected = f"Delete {org.name}"
    if body.confirmation != expected:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Confirmation text must be exactly: {expected}",
        )

    await org_service.delete(current_user.organization_id)
