<<<<<<< HEAD
"""Async SQLAlchemy engine + session factory for HRIP backend.

Creates a single async engine with asyncpg driver. Session lifecycle is
managed per-request by the get_db_session() dependency in dependencies.py.

Lifecycle:
    startup  → init_db()   called in main.py lifespan
    shutdown → close_db()  called in main.py lifespan

The engine is stored as a module-level singleton. Tests replace it with
an in-memory or test-database engine via override_engine().
"""
from __future__ import annotations

from collections.abc import AsyncGenerator
=======
"""Database session management.

This module provides the SQLAlchemy asynchronous engine and session maker
for connecting to the PostgreSQL database.
"""
from __future__ import annotations

from typing import AsyncGenerator
>>>>>>> d9048f63f52a0d37227ef395a75b662abc01e5c8

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
<<<<<<< HEAD
from sqlalchemy.orm import DeclarativeBase

from app.core.logging.logger import get_logger

log = get_logger(__name__)

# Module-level singletons — initialised in init_db(), never used before
_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


# ── ORM Base ──────────────────────────────────────────────────────────────────


class Base(DeclarativeBase):
    """Declarative base for all SQLAlchemy ORM models.

    All module models must inherit from this class:
        from app.core.database.session import Base

        class Patient(Base):
            __tablename__ = "patients"
            ...
    """


# ── Engine lifecycle ──────────────────────────────────────────────────────────


async def init_db(
    *,
    database_url: str,
    pool_size: int = 10,
    max_overflow: int = 20,
    echo: bool = False,
) -> None:
    """Create the async engine and session factory.

    Called once during application startup (lifespan).

    Args:
        database_url: asyncpg-compatible PostgreSQL URL, e.g.:
            "postgresql+asyncpg://user:pass@host/dbname"
        pool_size: Number of persistent connections in the pool.
        max_overflow: Extra connections allowed beyond pool_size.
        echo: If True, SQLAlchemy logs all SQL statements (dev only).
    """
    global _engine, _session_factory

    _engine = create_async_engine(
        database_url,
        pool_size=pool_size,
        max_overflow=max_overflow,
        echo=echo,
        # Return connections to the pool immediately on close rather than
        # waiting for the pool to evict them
        pool_pre_ping=True,
        pool_recycle=3600,  # Recycle connections after 1 hour
    )

    _session_factory = async_sessionmaker(
        _engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )

    log.info("database_connected", pool_size=pool_size, max_overflow=max_overflow)


async def close_db() -> None:
    """Dispose the async engine connection pool.

    Called during application shutdown (lifespan).
    """
    global _engine, _session_factory
    if _engine:
        await _engine.dispose()
        _engine = None
        _session_factory = None
        log.info("database_disconnected")


# ── Session factory accessors ─────────────────────────────────────────────────


def get_engine() -> AsyncEngine:
    """Return the active async engine.

    Raises:
        RuntimeError: If init_db() has not been called yet.
    """
    if _engine is None:
        raise RuntimeError("Database engine is not initialised. Call init_db() first.")
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Return the session factory.

    Raises:
        RuntimeError: If init_db() has not been called yet.
    """
    if _session_factory is None:
        raise RuntimeError("Session factory is not initialised. Call init_db() first.")
    return _session_factory


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency: yield an async database session per request.

    Usage:
        @router.get("/patients")
        async def list_patients(session: AsyncSession = Depends(get_db_session)):
            ...

    The session is committed on success and rolled back on exception.
    """
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# ── Test helper ───────────────────────────────────────────────────────────────


def override_engine(engine: AsyncEngine) -> None:
    """Replace the module-level engine for testing.

    Called in conftest.py to point the app at a test database.

    Args:
        engine: A test-scoped async engine.
    """
    global _engine, _session_factory
    _engine = engine
    _session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )
=======

from app.config import get_settings

settings = get_settings()

# Create the async engine
# The URL must be an async driver URL (e.g., postgresql+asyncpg://...)
engine: AsyncEngine = create_async_engine(
    str(settings.DATABASE_URL),
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    echo=settings.DEBUG,
)

# Create the async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get an async database session per request.

    Yields:
        AsyncSession: The database session.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
>>>>>>> d9048f63f52a0d37227ef395a75b662abc01e5c8
