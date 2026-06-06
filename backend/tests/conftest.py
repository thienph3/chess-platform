"""Shared test fixtures."""
import os
os.environ["TESTING"] = "1"

from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.db.session import get_db
from app.main import app
from app.shared.base_model import Base

TEST_DB_URL = settings.DATABASE_URL.replace("/vcc_platform", "/vcc_platform_test")


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create fresh tables, seed AI member, yield session, drop tables."""
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        # Seed AI member (required for AI games FK constraint)
        from app.modules.games.ai_router import AI_PLAYER_ID
        from app.modules.members.models import Member
        ai_member = Member(id=AI_PLAYER_ID, full_name="VCC Bot", email="ai@vcc.local")
        session.add(ai_member)
        await session.commit()

    async with session_factory() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    # Store session factory for creating new sessions per request
    engine = create_async_engine(TEST_DB_URL, echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    app.state.testing = True  # Disable rate limiting
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.state.testing = False
    app.dependency_overrides.clear()
    await engine.dispose()


@pytest_asyncio.fixture
async def auth_headers(client: AsyncClient) -> dict:
    """Register + login, return auth headers."""
    reg_resp = await client.post("/api/v1/auth/register", json={
        "email": "test@vinamilk.com.vn",
        "password": "testpass123",
        "full_name": "Test User",
    })
    assert reg_resp.status_code == 201, f"Register failed: {reg_resp.status_code} {reg_resp.text}"

    resp = await client.post("/api/v1/auth/login", json={
        "email": "test@vinamilk.com.vn",
        "password": "testpass123",
    })
    assert resp.status_code == 200, f"Login failed: {resp.status_code} {resp.text}"
    token = resp.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def second_user_headers(client: AsyncClient) -> dict:
    """Second user for multiplayer tests."""
    reg_resp = await client.post("/api/v1/auth/register", json={
        "email": "player2@vinamilk.com.vn",
        "password": "testpass123",
        "full_name": "Player Two",
    })
    assert reg_resp.status_code == 201, f"Register failed: {reg_resp.status_code} {reg_resp.text}"

    resp = await client.post("/api/v1/auth/login", json={
        "email": "player2@vinamilk.com.vn",
        "password": "testpass123",
    })
    assert resp.status_code == 200, f"Login failed: {resp.status_code} {resp.text}"
    token = resp.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}
