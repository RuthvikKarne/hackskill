"""HRIP Backend — FastAPI Application Entry Point.

This module initialises the FastAPI application, registers middleware,
mounts all module routers, and configures lifespan events (startup/shutdown).

ADDING A NEW MODULE:
1. Create backend/app/modules/<name>/ with standard structure.
2. Import and register the router below.
3. Register event subscriptions in the lifespan function.
4. No other files should need modification.
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis

from app.config import get_settings
from app.core.database.session import get_db_session
from app.core.database.redis import get_redis
from app.core.exceptions.handlers import add_exception_handlers
from app.core.logging.logger import setup_logging
from app.core.security.middleware import JWTMiddleware, RequestIDMiddleware
from app.core.security.limiter import setup_rate_limiter
from typing import Any

# ── Module routers will be imported here as they are implemented ──────────────
from app.modules.auth.router import router as auth_router
from app.modules.users.router import router as users_router
from app.modules.hospitals.router import router as hospitals_router
from app.modules.patients.router import router as patients_router
from app.modules.inventory.router import router as inventory_router
from app.modules.beds.router import router as beds_router
from app.modules.doctors.router import router as doctors_router
from app.modules.laboratory.router import router as laboratory_router
from app.modules.notifications.router import router as notifications_router
from app.modules.audit.router import router as audit_router
from app.modules.analytics.router import router as analytics_router
from app.modules.reports.router import router as reports_router
from app.modules.emergency.router import router as emergency_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan — runs on startup and shutdown.

    Startup:
    - Connect to PostgreSQL
    - Connect to Redis
    - Initialize Event Bus and register all subscribers
    - Warm up AI engine connection

    Shutdown:
    - Close database connections
    - Close Redis connections
    - Drain event bus
    """
    from app.modules.notifications.listeners import setup_listeners as setup_notification_listeners
    from app.modules.audit.listeners import setup_listeners as setup_audit_listeners
    
    setup_notification_listeners()
    setup_audit_listeners()
    settings = get_settings()

    # ── Startup ────────────────────────────────────────────────────────────────
    # TODO Phase 1: Initialize Redis connection
    # TODO Phase 1: Initialize Event Bus
    # TODO Phase 1: Register event subscriptions
    # DB engine is initialized globally in session.py upon import, we don't need explicit startup unless we test connections.

    yield  # Application runs here

    # ── Shutdown ───────────────────────────────────────────────────────────────
    from app.core.database.session import engine
    await engine.dispose()
    
    # TODO Phase 1: Close Redis
    # TODO Phase 1: Drain event bus


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    
    # Initialize structured logging
    setup_logging(json_logs=(settings.ENVIRONMENT == "production"))

    app = FastAPI(
        title="HRIP — Healthcare Resource Intelligence Platform",
        description="AI-powered healthcare resource management for public health facilities.",
        version=settings.APP_VERSION,
        docs_url="/api/docs" if settings.ENVIRONMENT != "production" else None,
        redoc_url="/api/redoc" if settings.ENVIRONMENT != "production" else None,
        lifespan=lifespan,
    )

    # ── Middleware ─────────────────────────────────────────────────────────────
    # Middlewares are executed bottom-up in Starlette.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    )
    
    # Rate Limiter setup (adds state.limiter and exception handler)
    setup_rate_limiter(app)
    
    app.add_middleware(JWTMiddleware)
    app.add_middleware(RequestIDMiddleware)
    
    # Register global exception handlers
    add_exception_handlers(app)

    # ── Routers ───────────────────────────────────────────────────────────────
    # Uncomment as each module is implemented:
    app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
    app.include_router(users_router, prefix="/api/v1/users", tags=["Users"])
    app.include_router(hospitals_router, prefix="/api/v1/hospitals", tags=["Hospitals"])
    app.include_router(patients_router, prefix="/api/v1/patients", tags=["Patients"])
    app.include_router(inventory_router, prefix="/api/v1/inventory", tags=["Inventory"])
    app.include_router(beds_router, prefix="/api/v1/beds", tags=["Beds"])
    app.include_router(doctors_router, prefix="/api/v1/doctors", tags=["Doctors"])
    app.include_router(laboratory_router, prefix="/api/v1/laboratory", tags=["Laboratory"])
    app.include_router(notifications_router, prefix="/api/v1/notifications", tags=["Notifications"])
    app.include_router(audit_router, prefix="/api/v1/audit", tags=["Audit"])
    app.include_router(analytics_router, prefix="/api/v1/analytics", tags=["Analytics"])
    app.include_router(reports_router, prefix="/api/v1/reports", tags=["Reports"])
    app.include_router(emergency_router, prefix="/api/v1/emergency", tags=["Emergency"])

    # ── Health Check ───────────────────────────────────────────────────────────
    @app.get("/health", tags=["Health"])
    async def health() -> dict[str, str]:
        """Basic health check — confirms the API process is running."""
        return {"status": "healthy", "service": "hrip-backend"}

    @app.get("/ready", tags=["Health"])
    async def ready(
        db: AsyncSession = Depends(get_db_session),
        redis_client: redis.Redis = Depends(get_redis)
    ) -> dict[str, Any]:
        """Readiness check — confirms DB and Redis are reachable."""
        status = {"status": "ready", "checks": {}}
        
        # Check DB
        try:
            await db.execute(text("SELECT 1"))
            status["checks"]["database"] = "ok"
        except Exception as e:
            status["status"] = "error"
            status["checks"]["database"] = f"error: {e}"

        # Check Redis
        try:
            await redis_client.ping()
            status["checks"]["redis"] = "ok"
        except Exception as e:
            status["status"] = "error"
            status["checks"]["redis"] = f"error: {e}"

        return status

    return app


app = create_app()
