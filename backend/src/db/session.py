import ssl
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.config import settings

# Neon (and any TLS-only Postgres host) requires SSL.
# asyncpg resolves `sslmode` in the URL itself, but passing an explicit
# ssl context as a connect_arg is the safest cross-platform approach.
_connect_args: dict = {}
if settings.app_env == "production":
    _ssl_ctx = ssl.create_default_context()
    _connect_args = {"ssl": _ssl_ctx}

engine = create_async_engine(
    settings.database_url,
    echo=False,
    connect_args=_connect_args,
)

async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
