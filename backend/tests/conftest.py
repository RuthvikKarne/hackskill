"""Shared pytest fixtures for the HRIP backend test suite.

Provides:
    - Isolated async test client (httpx + FastAPI)
    - In-memory SQLite engine for fast test DB (no Postgres needed in CI)
    - Mock event bus for asserting event publication without side effects
    - Default test token payloads for each RBAC role
"""
from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database.session import Base, override_engine
from app.core.events.bus import InProcessEventBus, override_event_bus
from app.core.events.registry import EventRegistry
from app.core.security.jwt import TokenPayload
from app.main import app

# ── Event loop (session-scoped) ───────────────────────────────────────────────


@pytest.fixture(scope="session")
def event_loop():
    """Create a single event loop for the entire test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ── Test database (SQLite in-memory, per-session) ──────────────────────────────


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    """Create an async SQLite in-memory engine for the test session.

    Uses SQLite (not PostgreSQL) for speed in unit tests. Integration tests
    targeting Postgres-specific behaviour should use a separate fixture with
    a real Postgres test DB.
    """
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        connect_args={"check_same_thread": False},
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    override_engine(engine)
    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Yield an isolated async session per test, rolled back after each test."""
    factory = async_sessionmaker(test_engine, expire_on_commit=False)
    async with factory() as session:
        try:
            yield session
        finally:
            await session.rollback()


# ── Mock event bus ─────────────────────────────────────────────────────────────


@pytest.fixture
def mock_event_bus() -> InProcessEventBus:
    """Replace the module-level event bus with a fresh isolated instance.

    Tests can assert events were published:
        mock_event_bus.publish = AsyncMock()
        ...
        mock_event_bus.publish.assert_called_once()

    The fresh registry prevents cross-test handler pollution.
    """
    registry = EventRegistry()
    bus = InProcessEventBus(registry=registry)
    bus.publish = AsyncMock(wraps=bus.publish)  # type: ignore[method-assign]
    override_event_bus(bus)
    return bus


# ── Async HTTP test client ─────────────────────────────────────────────────────


@pytest_asyncio.fixture
async def client(test_engine) -> AsyncGenerator[AsyncClient, None]:
    """Yield an async HTTP test client pointed at the HRIP FastAPI app.

    The client does NOT start the full lifespan (DB/Redis), so infrastructure
    is provided by fixtures (test_engine, mock_event_bus, etc.).
    """
    async with AsyncClient(
        transport=ASGITransport(app=app),  # type: ignore[arg-type]
        base_url="http://testserver",
    ) as ac:
        yield ac


# ── Test token payloads (per role) ────────────────────────────────────────────


@pytest.fixture
def hospital_id() -> str:
    """Consistent hospital UUID for test assertions."""
    return str(uuid4())


@pytest.fixture
def system_admin_token(hospital_id: str) -> TokenPayload:
    """TokenPayload for a SYSTEM_ADMIN user."""
    from app.core.security.rbac import ROLE_PERMISSIONS, Roles
    return TokenPayload(
        sub=str(uuid4()),
        role=Roles.SYSTEM_ADMIN,
        hospital_id=hospital_id,
        permissions=list(ROLE_PERMISSIONS[Roles.SYSTEM_ADMIN]),
        jti=str(uuid4()),
    )


@pytest.fixture
def hospital_admin_token(hospital_id: str) -> TokenPayload:
    """TokenPayload for a HOSPITAL_ADMIN user."""
    from app.core.security.rbac import ROLE_PERMISSIONS, Roles
    return TokenPayload(
        sub=str(uuid4()),
        role=Roles.HOSPITAL_ADMIN,
        hospital_id=hospital_id,
        permissions=list(ROLE_PERMISSIONS[Roles.HOSPITAL_ADMIN]),
        jti=str(uuid4()),
    )


@pytest.fixture
def doctor_token(hospital_id: str) -> TokenPayload:
    """TokenPayload for a DOCTOR user."""
    from app.core.security.rbac import ROLE_PERMISSIONS, Roles
    return TokenPayload(
        sub=str(uuid4()),
        role=Roles.DOCTOR,
        hospital_id=hospital_id,
        permissions=list(ROLE_PERMISSIONS[Roles.DOCTOR]),
        jti=str(uuid4()),
    )
