import uuid
from datetime import datetime, timedelta, timezone
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.config import settings
from src.models import Base, Organization, User, UserRole, UserStatus, Invitation, InvitationStatus
from src.auth.jwt import create_access_token

TEST_DATABASE_URL = settings.database_url

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
test_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db() -> AsyncGenerator[AsyncSession, None]:
    async with test_session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def sample_org(db: AsyncSession) -> Organization:
    org = Organization(name="Acme Corp")
    db.add(org)
    await db.flush()
    return org


@pytest_asyncio.fixture
async def sample_admin(db: AsyncSession, sample_org: Organization) -> User:
    user = User(
        organization_id=sample_org.id,
        email="admin@acme.com",
        name="Admin User",
        role=UserRole.ADMIN,
        status=UserStatus.ACTIVE,
    )
    db.add(user)
    await db.flush()
    return user


@pytest_asyncio.fixture
async def sample_manager(db: AsyncSession, sample_org: Organization) -> User:
    user = User(
        organization_id=sample_org.id,
        email="manager@acme.com",
        name="Manager User",
        role=UserRole.MANAGER,
        status=UserStatus.ACTIVE,
    )
    db.add(user)
    await db.flush()
    return user


@pytest_asyncio.fixture
async def sample_viewer(db: AsyncSession, sample_org: Organization) -> User:
    user = User(
        organization_id=sample_org.id,
        email="viewer@acme.com",
        name="Viewer User",
        role=UserRole.VIEWER,
        status=UserStatus.ACTIVE,
    )
    db.add(user)
    await db.flush()
    return user


@pytest_asyncio.fixture
async def other_org(db: AsyncSession) -> Organization:
    org = Organization(name="Other Inc")
    db.add(org)
    await db.flush()
    return org


@pytest_asyncio.fixture
async def other_org_admin(db: AsyncSession, other_org: Organization) -> User:
    user = User(
        organization_id=other_org.id,
        email="admin@other.com",
        name="Other Admin",
        role=UserRole.ADMIN,
        status=UserStatus.ACTIVE,
    )
    db.add(user)
    await db.flush()
    return user


@pytest_asyncio.fixture
async def sample_invitation(db: AsyncSession, sample_org: Organization, sample_admin: User) -> Invitation:
    invitation = Invitation(
        organization_id=sample_org.id,
        email="invitee@acme.com",
        name="Invitee User",
        role=UserRole.VIEWER,
        token="test-token-12345",
        invited_by=sample_admin.id,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )
    db.add(invitation)
    await db.flush()
    return invitation


@pytest_asyncio.fixture
async def expired_invitation(db: AsyncSession, sample_org: Organization, sample_admin: User) -> Invitation:
    invitation = Invitation(
        organization_id=sample_org.id,
        email="expired@acme.com",
        name="Expired Invitee",
        role=UserRole.VIEWER,
        token="expired-token-12345",
        invited_by=sample_admin.id,
        expires_at=datetime.now(timezone.utc) - timedelta(days=1),
    )
    db.add(invitation)
    await db.flush()
    return invitation


def make_auth_header(user: User) -> dict[str, str]:
    token = create_access_token(user.id, user.organization_id)
    return {"Authorization": f"Bearer {token}"}
