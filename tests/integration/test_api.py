import uuid

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession

from src.main import app
from src.models import User, UserRole, Organization, Invitation
from src.auth.jwt import create_access_token, create_refresh_token
from src.db import get_db


@pytest_asyncio.fixture
async def client(db: AsyncSession) -> AsyncClient:
    async def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.pop(get_db, None)


def auth_header(user: User) -> dict[str, str]:
    token = create_access_token(user.id, user.organization_id)
    return {"Authorization": f"Bearer {token}"}


class TestHealthRoutes:
    async def test_health_check(self, client: AsyncClient):
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    async def test_db_health_check(self, client: AsyncClient):
        response = await client.get("/health/db")
        assert response.status_code == 200
        assert response.json()["database"] == "connected"


class TestAuthRoutes:
    async def test_google_auth_url_register(self, client: AsyncClient):
        response = await client.get("/auth/google", params={"flow": "register", "org_name": "Acme"})
        assert response.status_code == 200
        assert "auth_url" in response.json()

    async def test_google_auth_url_login(self, client: AsyncClient):
        response = await client.get("/auth/google", params={"flow": "login"})
        assert response.status_code == 200
        assert "auth_url" in response.json()

    async def test_google_auth_url_invite(self, client: AsyncClient):
        response = await client.get("/auth/google", params={"flow": "invite", "invitation_token": "some-token"})
        assert response.status_code == 200
        assert "auth_url" in response.json()

    async def test_google_auth_invalid_flow(self, client: AsyncClient):
        response = await client.get("/auth/google", params={"flow": "invalid"})
        assert response.status_code == 422

    async def test_refresh_without_cookie(self, client: AsyncClient):
        response = await client.post("/auth/refresh")
        assert response.status_code == 401

    async def test_logout(self, client: AsyncClient):
        response = await client.post("/auth/logout")
        assert response.status_code == 200
        assert response.json()["message"] == "Logged out successfully"

    async def test_refresh_with_valid_cookie(self, client: AsyncClient, sample_admin: User):
        refresh = create_refresh_token(sample_admin.id, sample_admin.organization_id)
        client.cookies.set("refresh_token", refresh)
        response = await client.post("/auth/refresh")
        assert response.status_code == 200
        assert "access_token" in response.json()


class TestUserRoutes:
    async def test_list_users_authenticated(self, client: AsyncClient, sample_admin: User):
        response = await client.get("/users", headers=auth_header(sample_admin))
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    async def test_list_users_unauthenticated(self, client: AsyncClient):
        response = await client.get("/users")
        assert response.status_code in (401, 403)

    async def test_get_me(self, client: AsyncClient, sample_admin: User):
        response = await client.get("/users/me", headers=auth_header(sample_admin))
        assert response.status_code == 200
        assert response.json()["email"] == "admin@acme.com"

    async def test_update_role_as_manager(self, client: AsyncClient, sample_manager: User, sample_viewer: User):
        response = await client.patch(
            f"/users/{sample_viewer.id}/role",
            json={"role": "manager"},
            headers=auth_header(sample_manager),
        )
        assert response.status_code == 200
        assert response.json()["role"] == "manager"

    async def test_update_role_as_viewer_forbidden(self, client: AsyncClient, sample_viewer: User, sample_manager: User):
        response = await client.patch(
            f"/users/{sample_manager.id}/role",
            json={"role": "admin"},
            headers=auth_header(sample_viewer),
        )
        assert response.status_code == 403

    async def test_delete_user_as_admin(self, client: AsyncClient, sample_admin: User, sample_viewer: User):
        response = await client.delete(f"/users/{sample_viewer.id}", headers=auth_header(sample_admin))
        assert response.status_code == 204

    async def test_delete_user_as_manager_forbidden(self, client: AsyncClient, sample_manager: User, sample_viewer: User):
        response = await client.delete(f"/users/{sample_viewer.id}", headers=auth_header(sample_manager))
        assert response.status_code == 403

    async def test_delete_user_as_viewer_forbidden(self, client: AsyncClient, sample_viewer: User, sample_admin: User):
        response = await client.delete(f"/users/{sample_admin.id}", headers=auth_header(sample_viewer))
        assert response.status_code == 403


class TestInvitationRoutes:
    async def test_create_invitation_as_manager(self, client: AsyncClient, sample_manager: User):
        response = await client.post(
            "/invitations",
            json={"email": "newhire@acme.com", "name": "New Hire", "role": "viewer"},
            headers=auth_header(sample_manager),
        )
        assert response.status_code == 201
        assert response.json()["email"] == "newhire@acme.com"
        assert response.json()["token"] is not None

    async def test_create_invitation_as_admin(self, client: AsyncClient, sample_admin: User):
        response = await client.post(
            "/invitations",
            json={"email": "another@acme.com", "name": "Another", "role": "manager"},
            headers=auth_header(sample_admin),
        )
        assert response.status_code == 201

    async def test_create_invitation_as_viewer_forbidden(self, client: AsyncClient, sample_viewer: User):
        response = await client.post(
            "/invitations",
            json={"email": "blocked@acme.com", "name": "Blocked", "role": "viewer"},
            headers=auth_header(sample_viewer),
        )
        assert response.status_code == 403

    async def test_list_pending_as_manager(self, client: AsyncClient, sample_manager: User, sample_invitation: Invitation):
        response = await client.get("/invitations", headers=auth_header(sample_manager))
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    async def test_list_pending_as_viewer_forbidden(self, client: AsyncClient, sample_viewer: User):
        response = await client.get("/invitations", headers=auth_header(sample_viewer))
        assert response.status_code == 403

    async def test_create_with_invalid_email(self, client: AsyncClient, sample_admin: User):
        response = await client.post(
            "/invitations",
            json={"email": "not-an-email", "name": "Bad", "role": "viewer"},
            headers=auth_header(sample_admin),
        )
        assert response.status_code == 422

    async def test_create_with_missing_fields(self, client: AsyncClient, sample_admin: User):
        response = await client.post(
            "/invitations",
            json={},
            headers=auth_header(sample_admin),
        )
        assert response.status_code == 422


class TestMultiTenancyIsolation:
    async def test_users_only_see_own_org(self, client: AsyncClient, sample_admin: User, other_org_admin: User):
        response = await client.get("/users", headers=auth_header(sample_admin))
        emails = [u["email"] for u in response.json()]
        assert "admin@acme.com" in emails
        assert "admin@other.com" not in emails

    async def test_cannot_update_role_cross_org(self, client: AsyncClient, sample_viewer: User, other_org_admin: User):
        response = await client.patch(
            f"/users/{sample_viewer.id}/role",
            json={"role": "admin"},
            headers=auth_header(other_org_admin),
        )
        assert response.status_code == 403

    async def test_cannot_delete_cross_org(self, client: AsyncClient, sample_viewer: User, other_org_admin: User):
        response = await client.delete(
            f"/users/{sample_viewer.id}",
            headers=auth_header(other_org_admin),
        )
        assert response.status_code == 403
