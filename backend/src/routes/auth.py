import json
import uuid
from typing import Annotated
from urllib.parse import urlencode

import jwt as pyjwt
from fastapi import APIRouter, Depends, HTTPException, Query, Response, Cookie, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.db import get_db
from src.auth.oauth import build_google_auth_url, exchange_code_for_tokens, get_google_user_info
from src.auth.jwt import create_access_token, create_refresh_token, verify_refresh_token
from src.services import OrganizationService, UserService, InvitationService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/google")
async def google_auth(
    flow: str = Query(..., regex="^(register|login|invite)$"),
    org_name: str | None = Query(None),
    invitation_token: str | None = Query(None),
):
    state_data = {"flow": flow}
    if flow == "register" and org_name:
        state_data["org_name"] = org_name
    if flow == "invite" and invitation_token:
        state_data["invitation_token"] = invitation_token

    state = json.dumps(state_data)
    auth_url = build_google_auth_url(state)
    return {"auth_url": auth_url}


@router.get("/callback")
async def google_callback(
    code: str = Query(...),
    state: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    state_data = json.loads(state)
    flow = state_data.get("flow")

    tokens = await exchange_code_for_tokens(code)
    google_access_token = tokens.get("access_token")
    if not google_access_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to get access token from Google")

    user_info = await get_google_user_info(google_access_token)
    email = user_info.get("email")
    name = user_info.get("name", "")
    picture = user_info.get("picture")

    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email not provided by Google")

    if flow == "register":
        org_name = state_data.get("org_name")
        if not org_name:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Organization name is required for registration")

        user_service = UserService(db)
        existing = await user_service.get_by_email(email)
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with this email already exists")

        org_service = OrganizationService(db)
        org, user = await org_service.register(
            org_name=org_name, admin_email=email, admin_name=name, profile_picture=picture
        )

    elif flow == "login":
        user_service = UserService(db)
        user = await user_service.get_by_email(email)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No account found for this email")

        await user_service.activate_user(user, name=name, profile_picture=picture)

    elif flow == "invite":
        invitation_token = state_data.get("invitation_token")
        if not invitation_token:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invitation token is required")

        invitation_service = InvitationService(db)
        user = await invitation_service.accept_invitation(
            token=invitation_token, oauth_email=email, oauth_name=name, profile_picture=picture
        )

    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid auth flow")

    access_token = create_access_token(user.id, user.organization_id)
    refresh_token = create_refresh_token(user.id, user.organization_id)

    redirect_url = f"{settings.frontend_url}/auth/callback?{urlencode({'access_token': access_token})}"

    response = RedirectResponse(url=redirect_url)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.app_env != "development",
        samesite="lax",
        max_age=settings.jwt_refresh_token_expire_days * 24 * 60 * 60,
    )
    return response


@router.post("/refresh")
async def refresh_access_token(
    refresh_token: Annotated[str | None, Cookie()] = None,
    db: AsyncSession = Depends(get_db),
):
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token not found")

    try:
        payload = verify_refresh_token(refresh_token)
    except pyjwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")

    user_id = uuid.UUID(payload["sub"])
    org_id = uuid.UUID(payload["org"])

    user_service = UserService(db)
    user = await user_service.get_by_id(user_id)

    new_access_token = create_access_token(user.id, user.organization_id)
    new_refresh_token = create_refresh_token(user.id, user.organization_id)

    response = Response(
        content=json.dumps({"access_token": new_access_token}),
        media_type="application/json",
    )
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=settings.app_env != "development",
        samesite="lax",
        max_age=settings.jwt_refresh_token_expire_days * 24 * 60 * 60,
    )
    return response


@router.post("/logout")
async def logout():
    response = Response(
        content=json.dumps({"message": "Logged out successfully"}),
        media_type="application/json",
    )
    response.delete_cookie(key="refresh_token")
    return response
