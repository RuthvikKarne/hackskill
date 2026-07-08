"""Background job worker for HRIP backend.

This module configures the `arq` worker, which processes asynchronous tasks
such as heavy AI computations, email notifications, and cron jobs.

To run the worker:
    arq app.worker.WorkerSettings
"""
from __future__ import annotations

import asyncio
from typing import Any

from arq import cron
from arq.connections import RedisSettings
from sqlalchemy import text

from app.config import get_settings
from app.core.database.session import close_db, init_db, get_session_factory
from app.core.logging.logger import get_logger

log = get_logger(__name__)
settings = get_settings()


# ── Background Tasks ──────────────────────────────────────────────────────────


async def sync_ai_recommendations(ctx: dict[str, Any]) -> str:
    """Cron job: Sync AI recommendations from the AI engine into the DB.
    
    This avoids blocking the main API thread and allows us to pre-compute
    heavy analytical queries.
    """
    log.info("task_started", task="sync_ai_recommendations")
    # TODO: Fetch from AI engine and write to PostgreSQL
    await asyncio.sleep(2)
    log.info("task_completed", task="sync_ai_recommendations")
    return "success"


async def generate_hospital_daily_report(ctx: dict[str, Any], hospital_id: str) -> None:
    """Background task: Generate daily PDF report for a hospital."""
    log.info("task_started", task="generate_hospital_daily_report", hospital_id=hospital_id)
    # TODO: Pull metrics, generate PDF, upload to storage
    await asyncio.sleep(5)
    log.info("task_completed", task="generate_hospital_daily_report", hospital_id=hospital_id)


# ── Database Cleanup Task ─────────────────────────────────────────────────────


async def cleanup_expired_sessions(ctx: dict[str, Any]) -> str:
    """Cron job: Delete expired refresh tokens or stale sessions."""
    log.info("task_started", task="cleanup_expired_sessions")
    
    factory = get_session_factory()
    async with factory() as session:
        # Example query (adjust based on actual schema)
        # await session.execute(text("DELETE FROM sessions WHERE expires_at < NOW()"))
        # await session.commit()
        pass
        
    log.info("task_completed", task="cleanup_expired_sessions")
    return "cleaned"


# ── Worker Lifecycle ──────────────────────────────────────────────────────────


async def startup(ctx: dict[str, Any]) -> None:
    """Initialize DB and connections when the worker starts."""
    log.info("worker_startup")
    db_url = str(settings.DATABASE_URL).replace("postgresql://", "postgresql+asyncpg://", 1)
    await init_db(
        database_url=db_url,
        pool_size=5,  # Worker needs fewer connections
        max_overflow=10,
    )
    # Store HTTP client or other shared resources in ctx if needed
    ctx["http_client"] = None  # Placeholder


async def shutdown(ctx: dict[str, Any]) -> None:
    """Cleanup resources when the worker shuts down."""
    log.info("worker_shutdown")
    await close_db()


# ── Worker Configuration ──────────────────────────────────────────────────────


class WorkerSettings:
    """Configuration for the arq worker.
    
    The arq CLI looks for this class to configure the worker.
    """
    
    # Parse redis URL. Example: redis://localhost:6379/0
    redis_settings = RedisSettings.from_dsn(str(settings.REDIS_URL))
    
    # Functions that can be enqueued manually
    functions = [
        generate_hospital_daily_report,
    ]
    
    # Scheduled cron jobs
    cron_jobs = [
        # Run AI sync every hour
        cron(sync_ai_recommendations, minute=0),
        # Run cleanup at 3:00 AM every day
        cron(cleanup_expired_sessions, hour=3, minute=0),
    ]
    
    on_startup = startup
    on_shutdown = shutdown
    
    max_jobs = 10
    job_timeout = 300  # 5 minutes max
