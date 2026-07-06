"""Shared FastAPI dependencies.

These are injected into route handlers via FastAPI's Depends() system.
Do not add business logic here — only infrastructure dependencies.

Dependency reference:
    get_db_session()   → AsyncSession    (one per request, auto commit/rollback)
    get_current_user() → TokenPayload    (JWT claims from Bearer header OR cookie)
    get_event_bus()    → InProcessEventBus
    get_redis()        → Redis           (shared client from main.py)

Usage in a router:
    from sqlalchemy.ext.asyncio import AsyncSession
    from fastapi import Depends
    from app.dependencies import get_db_session, get_current_user
    from app.core.security.jwt import TokenPayload

    @router.get("/patients")
    async def list_patients(
        session: AsyncSession = Depends(get_db_session),
        current_user: TokenPayload = Depends(get_current_user),
    ):
        ...
"""
from __future__ import annotations

from collections.abc import AsyncGenerator

import redis.asyncio as aioredis
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_db_session as _get_db_session
from app.core.events.bus import InProcessEventBus
from app.core.events.bus import get_event_bus as _get_event_bus
from app.core.exceptions.base import AuthenticationError
from app.core.security.jwt import TokenPayload


# ── Database session ──────────────────────────────────────────────────────────


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield a request-scoped async database session.

    Commits on success, rolls back on exception.
    Session is automatically closed when the request ends.

    Yields:
        AsyncSession: SQLAlchemy async session scoped to this request.
    """
    async for session in _get_db_session():
        yield session


# ── Current authenticated user ────────────────────────────────────────────────


async def get_current_user(request: Request) -> TokenPayload:
    """Return the authenticated user's token payload.

    The JWT has already been validated by JWTAuthMiddleware and stored in
    request.state.user. This dependency simply surfaces it as a typed object
    for route handlers.

    Both Bearer token and HttpOnly cookie sources are supported transparently
    — the middleware handles extraction, this dependency just reads the result.

    Args:
        request: Incoming FastAPI request.

    Returns:
        TokenPayload with all JWT claims (sub, role, hospital_id, permissions).

    Raises:
        AuthenticationError: If no authenticated user is present in the
            request state (should not happen on protected routes, but guards
            against misconfigured public route access).
    """
    user: TokenPayload | None = getattr(request.state, "user", None)
    if user is None:
        raise AuthenticationError("Authentication required.")
    return user


# ── Event bus ─────────────────────────────────────────────────────────────────


async def get_event_bus() -> InProcessEventBus:
    """Return the application event bus.

    Services use this to publish domain events. The bus dispatches to all
    registered handlers concurrently.

    Returns:
        InProcessEventBus singleton (Kafka-ready interface).
    """
    return _get_event_bus()


# ── Redis ─────────────────────────────────────────────────────────────────────


async def get_redis() -> aioredis.Redis:
    """Return the shared Redis client.

    Used by the auth module (token blocklist, refresh token store) and
    the rate limiter.

    Returns:
        aioredis.Redis client connected at application startup.
    """
    from app.main import get_redis_client
    return get_redis_client()
