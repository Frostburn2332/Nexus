import uuid
from datetime import datetime, timedelta, timezone

import jwt as pyjwt
import pytest

from src.config import settings
from src.auth.jwt import (
    ALGORITHM,
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_access_token,
    verify_refresh_token,
)


@pytest.fixture
def user_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def org_id() -> uuid.UUID:
    return uuid.uuid4()


class TestTokenCreation:
    def test_create_access_token(self, user_id, org_id):
        token = create_access_token(user_id, org_id)
        payload = decode_token(token)
        assert payload["sub"] == str(user_id)
        assert payload["org"] == str(org_id)
        assert payload["type"] == "access"

    def test_create_refresh_token(self, user_id, org_id):
        token = create_refresh_token(user_id, org_id)
        payload = decode_token(token)
        assert payload["sub"] == str(user_id)
        assert payload["org"] == str(org_id)
        assert payload["type"] == "refresh"

    def test_access_token_has_expiry(self, user_id, org_id):
        token = create_access_token(user_id, org_id)
        payload = decode_token(token)
        assert "exp" in payload

    def test_refresh_token_has_expiry(self, user_id, org_id):
        token = create_refresh_token(user_id, org_id)
        payload = decode_token(token)
        assert "exp" in payload


class TestTokenVerification:
    def test_verify_valid_access_token(self, user_id, org_id):
        token = create_access_token(user_id, org_id)
        payload = verify_access_token(token)
        assert payload["sub"] == str(user_id)

    def test_verify_valid_refresh_token(self, user_id, org_id):
        token = create_refresh_token(user_id, org_id)
        payload = verify_refresh_token(token)
        assert payload["sub"] == str(user_id)


class TestTokenRejection:
    def test_reject_refresh_as_access(self, user_id, org_id):
        token = create_refresh_token(user_id, org_id)
        with pytest.raises(pyjwt.InvalidTokenError, match="Not an access token"):
            verify_access_token(token)

    def test_reject_access_as_refresh(self, user_id, org_id):
        token = create_access_token(user_id, org_id)
        with pytest.raises(pyjwt.InvalidTokenError, match="Not a refresh token"):
            verify_refresh_token(token)

    def test_reject_expired_token(self, user_id, org_id):
        payload = {
            "sub": str(user_id),
            "org": str(org_id),
            "type": "access",
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
            "iat": datetime.now(timezone.utc) - timedelta(minutes=16),
        }
        token = pyjwt.encode(payload, settings.jwt_secret_key, algorithm=ALGORITHM)
        with pytest.raises(pyjwt.ExpiredSignatureError):
            decode_token(token)

    def test_reject_wrong_secret(self, user_id, org_id):
        payload = {
            "sub": str(user_id),
            "org": str(org_id),
            "type": "access",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
        }
        token = pyjwt.encode(payload, "wrong-secret", algorithm=ALGORITHM)
        with pytest.raises(pyjwt.InvalidSignatureError):
            decode_token(token)

    def test_reject_tampered_token(self, user_id, org_id):
        token = create_access_token(user_id, org_id)
        tampered = token[:-5] + "XXXXX"
        with pytest.raises(pyjwt.InvalidTokenError):
            decode_token(tampered)
