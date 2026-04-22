from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.security import create_access_token, get_password_hash
from app.db.database import Base, get_db
from app.main import app
from app.models.user import User

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def db_session():
    """DB SQLite in-memory isolato per ogni test."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session
    await engine.dispose()


@pytest_asyncio.fixture
async def client(db_session):
    """AsyncClient FastAPI con DB di test e startup mockato."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    mock_conn = AsyncMock()
    mock_conn.run_sync = AsyncMock()
    mock_ctx = MagicMock()
    mock_ctx.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_ctx.__aexit__ = AsyncMock(return_value=None)

    with (
        patch("app.main.engine.begin", return_value=mock_ctx),
        patch("app.main.scheduler") as mock_sched,
    ):
        mock_sched.running = False
        mock_sched.get_job.return_value = None
        mock_sched.start = MagicMock()
        mock_sched.add_job = MagicMock()
        mock_sched.shutdown = MagicMock()

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(db_session):
    """Utente di test preregistrato nel DB."""
    user = User(
        email="mario@example.com",
        username="mario",
        hashed_password=get_password_hash("password123"),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def auth_headers(test_user):
    """Header Authorization con JWT valido per test_user."""
    token = create_access_token(
        data={"sub": test_user.email},
        expires_delta=timedelta(minutes=30),
    )
    return {"Authorization": f"Bearer {token}"}
