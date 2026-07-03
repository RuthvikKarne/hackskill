"""Shared FastAPI dependencies.

These are injected into route handlers via FastAPI's Depends() system.
Do not add business logic here — only infrastructure dependencies.
"""
from __future__ import annotations

# TODO Phase 1: Add DB session dependency
# TODO Phase 1: Add current user dependency (JWT extraction)
# TODO Phase 1: Add event bus dependency
# TODO Phase 1: Add Redis dependency

# Example pattern (implemented in Phase 1):
#
# from sqlalchemy.ext.asyncio import AsyncSession
# from app.core.database.session import async_session_factory
#
# async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
#     async with async_session_factory() as session:
#         try:
#             yield session
#             await session.commit()
#         except Exception:
#             await session.rollback()
#             raise
