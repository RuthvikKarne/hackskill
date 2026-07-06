"""Alembic migration environment configuration.

This file is executed by Alembic for both online (live DB) and offline
(SQL script generation) migration modes.

Key design decisions:
    - DATABASE_URL is read from the HRIP Settings object (environment variable).
      Never hardcoded here.
    - Async migrations via asyncpg (run_async_migrations helper).
    - All module models must be imported here so Alembic can detect schema changes
      via autogenerate. Add imports as each module's models.py is implemented.

Adding a new module's models (Phase 3+):
    1. Import the module's models below the "Module model imports" section.
    2. Run: alembic revision --autogenerate -m "add_<module>_tables"
    3. Review the generated migration, then: alembic upgrade head
"""
from __future__ import annotations

import asyncio
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.core.database.session import Base

# ── Module model imports (add here as modules are implemented) ────────────────
# Phase 2:
# from app.modules.auth.models import User, Role, Permission, RefreshToken
# Phase 3:
# from app.modules.hospitals.models import Hospital, Department, Ward
# from app.modules.patients.models import Patient, Visit
# from app.modules.inventory.models import Medicine, Stock, PurchaseOrder
# from app.modules.beds.models import Bed, BedAllocation
# from app.modules.doctors.models import Doctor, Shift
# from app.modules.laboratory.models import LabTest, LabResult

# ── Alembic config setup ──────────────────────────────────────────────────────

# The alembic.Config object provides access to values in alembic.ini
config = context.config

# Configure Python logging from the ini file (if present)
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set the SQLAlchemy metadata for autogenerate support
target_metadata = Base.metadata

# ── Database URL injection (from environment) ─────────────────────────────────


def _get_database_url() -> str:
    """Return the database URL from the environment.

    Reads DATABASE_URL from the environment and converts it to asyncpg format.
    Never falls back to a default — misconfigured environments should fail loudly.

    Returns:
        asyncpg-compatible PostgreSQL URL.

    Raises:
        RuntimeError: If DATABASE_URL is not set.
    """
    url = os.environ.get("DATABASE_URL")
    if not url:
        # Try loading from the Settings object (which reads .env)
        try:
            from app.config import get_settings
            settings = get_settings()
            url = str(settings.DATABASE_URL)
        except Exception:
            raise RuntimeError(
                "DATABASE_URL environment variable is not set. "
                "Cannot run migrations without a database URL."
            )

    # Ensure asyncpg driver (alembic needs async driver for online mode)
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


# ── Offline migration mode (generates SQL without connecting) ─────────────────


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode — emits SQL to stdout.

    Used with: alembic upgrade head --sql > migrations.sql
    Useful for reviewing or applying migrations in environments where
    direct DB access from the migration runner is not available.
    """
    url = _get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


# ── Online migration mode (connects to the live DB) ───────────────────────────


def do_run_migrations(connection) -> None:
    """Execute migrations using the provided connection.

    Args:
        connection: An active database connection.
    """
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Create an async engine and run migrations asynchronously.

    Uses NullPool to avoid connection pooling during migrations (each
    migration run should have a fresh, short-lived connection).
    """
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = _get_database_url()

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Entry point for online migrations — runs the async loop."""
    asyncio.run(run_async_migrations())


# ── Mode dispatch ─────────────────────────────────────────────────────────────

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
