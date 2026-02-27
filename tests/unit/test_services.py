import uuid
from datetime import datetime, timedelta, timezone

import pytest
import pytest_asyncio
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Organization, User, UserRole, UserStatus, Invitation, InvitationStatus
from src.services import OrganizationService, UserService, InvitationService


class TestOrganizationService:
    async def test_register_creates_org_and_admin(self, db: AsyncSession):
        service = OrganizationService(db)
        org, admin = await service.register("Acme", "admin@acme.com", "Admin User")

        assert org.name == "Acme"
        assert admin.email == "admin@acme.com"
        assert admin.role == UserRole.ADMIN
        assert admin.status == UserStatus.ACTIVE
        assert admin.organization_id == org.id

    async def test_register_stores_profile_picture(self, db: AsyncSession):
        service = OrganizationService(db)
        _, admin = await service.register("Acme", "admin@acme.com", "Admin", profile_picture="https://pic.url")

        assert admin.profile_picture == "https://pic.url"

    async def test_get_by_id(self, db: AsyncSession, sample_org: Organization):
        service = OrganizationService(db)
        result = await service.get_by_id(sample_org.id)

        assert result is not None
        assert result.id == sample_org.id

    async def test_get_by_invalid_id(self, db: AsyncSession):
        service = OrganizationService(db)
        result = await service.get_by_id(uuid.uuid4())

        assert result is None


class TestUserService:
    async def test_get_by_id(self, db: AsyncSession, sample_admin: User):
        service = UserService(db)
        result = await service.get_by_id(sample_admin.id)

        assert result.id == sample_admin.id

    async def test_get_by_invalid_id_raises_404(self, db: AsyncSession):
        service = UserService(db)

        with pytest.raises(HTTPException) as exc:
            await service.get_by_id(uuid.uuid4())
        assert exc.value.status_code == 404

    async def test_get_by_email(self, db: AsyncSession, sample_admin: User):
        service = UserService(db)
        result = await service.get_by_email("admin@acme.com")

        assert result is not None
        assert result.email == "admin@acme.com"

    async def test_get_by_email_not_found(self, db: AsyncSession):
        service = UserService(db)
        result = await service.get_by_email("nobody@acme.com")

        assert result is None

    async def test_list_by_organization(self, db: AsyncSession, sample_org: Organization, sample_admin: User, sample_viewer: User):
        service = UserService(db)
        users = await service.list_by_organization(sample_org.id)

        assert len(users) >= 2
        emails = [u.email for u in users]
        assert "admin@acme.com" in emails
        assert "viewer@acme.com" in emails

    async def test_update_role(self, db: AsyncSession, sample_admin: User, sample_viewer: User):
        service = UserService(db)
        updated = await service.update_role(sample_viewer.id, UserRole.MANAGER, sample_admin)

        assert updated.role == UserRole.MANAGER

    async def test_cannot_change_own_role(self, db: AsyncSession, sample_admin: User):
        service = UserService(db)

        with pytest.raises(HTTPException) as exc:
            await service.update_role(sample_admin.id, UserRole.VIEWER, sample_admin)
        assert exc.value.status_code == 400

    async def test_cannot_change_role_cross_org(self, db: AsyncSession, sample_viewer: User, other_org_admin: User):
        service = UserService(db)

        with pytest.raises(HTTPException) as exc:
            await service.update_role(sample_viewer.id, UserRole.MANAGER, other_org_admin)
        assert exc.value.status_code == 403

    async def test_delete_user(self, db: AsyncSession, sample_admin: User, sample_viewer: User):
        service = UserService(db)
        await service.delete_user(sample_viewer.id, sample_admin)

        with pytest.raises(HTTPException) as exc:
            await service.get_by_id(sample_viewer.id)
        assert exc.value.status_code == 404

    async def test_cannot_delete_self(self, db: AsyncSession, sample_admin: User):
        service = UserService(db)

        with pytest.raises(HTTPException) as exc:
            await service.delete_user(sample_admin.id, sample_admin)
        assert exc.value.status_code == 400

    async def test_cannot_delete_cross_org(self, db: AsyncSession, sample_viewer: User, other_org_admin: User):
        service = UserService(db)

        with pytest.raises(HTTPException) as exc:
            await service.delete_user(sample_viewer.id, other_org_admin)
        assert exc.value.status_code == 403

    async def test_activate_user(self, db: AsyncSession, sample_org: Organization):
        pending_user = User(
            organization_id=sample_org.id,
            email="pending@acme.com",
            name="Pending",
            role=UserRole.VIEWER,
            status=UserStatus.PENDING,
        )
        db.add(pending_user)
        await db.flush()

        service = UserService(db)
        activated = await service.activate_user(pending_user, name="Updated Name", profile_picture="https://pic.url")

        assert activated.status == UserStatus.ACTIVE
        assert activated.name == "Updated Name"
        assert activated.profile_picture == "https://pic.url"


class TestInvitationService:
    async def test_create_invitation(self, db: AsyncSession, sample_org: Organization, sample_admin: User):
        service = InvitationService(db)
        invitation = await service.create_invitation(
            organization_id=sample_org.id,
            email="newuser@acme.com",
            name="New User",
            role=UserRole.VIEWER,
            invited_by=sample_admin.id,
        )

        assert invitation.email == "newuser@acme.com"
        assert invitation.status == InvitationStatus.PENDING
        assert invitation.token is not None
        assert len(invitation.token) > 0

    async def test_reject_duplicate_user(self, db: AsyncSession, sample_org: Organization, sample_admin: User):
        service = InvitationService(db)

        with pytest.raises(HTTPException) as exc:
            await service.create_invitation(
                organization_id=sample_org.id,
                email="admin@acme.com",
                name="Duplicate",
                role=UserRole.VIEWER,
                invited_by=sample_admin.id,
            )
        assert exc.value.status_code == 409

    async def test_reject_duplicate_pending_invitation(self, db: AsyncSession, sample_org: Organization, sample_admin: User, sample_invitation: Invitation):
        service = InvitationService(db)

        with pytest.raises(HTTPException) as exc:
            await service.create_invitation(
                organization_id=sample_org.id,
                email="invitee@acme.com",
                name="Duplicate Invite",
                role=UserRole.VIEWER,
                invited_by=sample_admin.id,
            )
        assert exc.value.status_code == 409

    async def test_accept_with_matching_email(self, db: AsyncSession, sample_invitation: Invitation):
        service = InvitationService(db)
        user = await service.accept_invitation(
            token="test-token-12345",
            oauth_email="invitee@acme.com",
            oauth_name="Invitee User",
        )

        assert user.email == "invitee@acme.com"
        assert user.status == UserStatus.ACTIVE
        assert user.role == UserRole.VIEWER

    async def test_accept_email_case_insensitive(self, db: AsyncSession, sample_invitation: Invitation):
        service = InvitationService(db)
        user = await service.accept_invitation(
            token="test-token-12345",
            oauth_email="Invitee@Acme.COM",
            oauth_name="Invitee User",
        )

        assert user.status == UserStatus.ACTIVE

    async def test_reject_mismatched_email(self, db: AsyncSession, sample_invitation: Invitation):
        service = InvitationService(db)

        with pytest.raises(HTTPException) as exc:
            await service.accept_invitation(
                token="test-token-12345",
                oauth_email="wrong@other.com",
                oauth_name="Wrong User",
            )
        assert exc.value.status_code == 401

    async def test_reject_expired_invitation(self, db: AsyncSession, expired_invitation: Invitation):
        service = InvitationService(db)

        with pytest.raises(HTTPException) as exc:
            await service.accept_invitation(
                token="expired-token-12345",
                oauth_email="expired@acme.com",
                oauth_name="Expired User",
            )
        assert exc.value.status_code == 400

    async def test_reject_already_accepted(self, db: AsyncSession, sample_invitation: Invitation):
        service = InvitationService(db)
        await service.accept_invitation(
            token="test-token-12345",
            oauth_email="invitee@acme.com",
            oauth_name="Invitee",
        )

        with pytest.raises(HTTPException) as exc:
            await service.accept_invitation(
                token="test-token-12345",
                oauth_email="invitee@acme.com",
                oauth_name="Invitee",
            )
        assert exc.value.status_code == 400

    async def test_reject_invalid_token(self, db: AsyncSession):
        service = InvitationService(db)

        with pytest.raises(HTTPException) as exc:
            await service.accept_invitation(
                token="nonexistent-token",
                oauth_email="someone@acme.com",
                oauth_name="Someone",
            )
        assert exc.value.status_code == 404

    async def test_accepted_user_has_correct_org(self, db: AsyncSession, sample_invitation: Invitation, sample_org: Organization):
        service = InvitationService(db)
        user = await service.accept_invitation(
            token="test-token-12345",
            oauth_email="invitee@acme.com",
            oauth_name="Invitee",
        )

        assert user.organization_id == sample_org.id

    async def test_accepted_user_has_assigned_role(self, db: AsyncSession, sample_org: Organization, sample_admin: User):
        service = InvitationService(db)
        invitation = await service.create_invitation(
            organization_id=sample_org.id,
            email="manager-invite@acme.com",
            name="Future Manager",
            role=UserRole.MANAGER,
            invited_by=sample_admin.id,
        )

        user = await service.accept_invitation(
            token=invitation.token,
            oauth_email="manager-invite@acme.com",
            oauth_name="Future Manager",
        )

        assert user.role == UserRole.MANAGER

    async def test_list_pending(self, db: AsyncSession, sample_org: Organization, sample_invitation: Invitation):
        service = InvitationService(db)
        pending = await service.list_pending(sample_org.id)

        assert len(pending) >= 1
        assert all(inv.status == InvitationStatus.PENDING for inv in pending)

    async def test_accepted_not_in_pending_list(self, db: AsyncSession, sample_org: Organization, sample_invitation: Invitation):
        service = InvitationService(db)
        await service.accept_invitation(
            token="test-token-12345",
            oauth_email="invitee@acme.com",
            oauth_name="Invitee",
        )

        pending = await service.list_pending(sample_org.id)
        tokens = [inv.token for inv in pending]
        assert "test-token-12345" not in tokens
