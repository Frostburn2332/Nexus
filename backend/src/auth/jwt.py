import uuid
from datetime import datetime, timedelta, timezone

import jwt

from src.config import settings

ALGORITHM = "HS256"


def create_access_token(user_id: uuid.UUID, organization_id: uuid.UUID) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.jwt_access_token_expire_minutes
    )
    payload = {
        "sub": str(user_id),
        "org": str(organization_id),
        "type": "access",
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=ALGORITHM)


def create_refresh_token(user_id: uuid.UUID, organization_id: uuid.UUID) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.jwt_refresh_token_expire_days
    )
    payload = {
        "sub": str(user_id),
        "org": str(organization_id),
        "type": "refresh",
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[ALGORITHM])


def verify_access_token(token: str) -> dict:
    payload = decode_token(token)
    if payload.get("type") != "access":
        raise jwt.InvalidTokenError("Not an access token")
    return payload


def verify_refresh_token(token: str) -> dict:
    payload = decode_token(token)
    if payload.get("type") != "refresh":
        raise jwt.InvalidTokenError("Not a refresh token")
    return payload
