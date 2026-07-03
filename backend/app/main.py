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

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings

# ── Module routers will be imported here as they are implemented ──────────────
# from app.modules.auth.router import router as auth_router
# from app.modules.users.router import router as users_router
# from app.modules.hospitals.router import router as hospitals_router
# from app.modules.patients.router import router as patients_router
# from app.modules.inventory.router import router as inventory_router
# from app.modules.beds.router import router as beds_router
# from app.modules.doctors.router import router as doctors_router
# from app.modules.laboratory.router import router as laboratory_router
# from app.modules.emergency.router import router as emergency_router
# from app.modules.notifications.router import router as notifications_router
# from app.modules.analytics.router import router as analytics_router
# from app.modules.reports.router import router as reports_router
# from app.modules.audit.router import router as audit_router


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
    settings = get_settings()

    # ── Startup ────────────────────────────────────────────────────────────────
    # TODO Phase 1: Initialize DB connection pool
    # TODO Phase 1: Initialize Redis connection
    # TODO Phase 1: Initialize Event Bus
    # TODO Phase 1: Register event subscriptions

    yield  # Application runs here

    # ── Shutdown ───────────────────────────────────────────────────────────────
    # TODO Phase 1: Close DB pool
    # TODO Phase 1: Close Redis
    # TODO Phase 1: Drain event bus


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="HRIP — Healthcare Resource Intelligence Platform",
        description="AI-powered healthcare resource management for public health facilities.",
        version=settings.APP_VERSION,
        docs_url="/api/docs" if settings.ENVIRONMENT != "production" else None,
        redoc_url="/api/redoc" if settings.ENVIRONMENT != "production" else None,
        lifespan=lifespan,
    )

    # ── Middleware ─────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    )

    # TODO Phase 1: Add JWT middleware
    # TODO Phase 1: Add RBAC middleware
    # TODO Phase 1: Add rate limiting middleware
    # TODO Phase 1: Add request ID middleware
    # TODO Phase 1: Add structured logging middleware
    # TODO Phase 1: Add global exception handler

    # ── Routers ───────────────────────────────────────────────────────────────
    # Uncomment as each module is implemented:
    # app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
    # app.include_router(users_router, prefix="/api/v1/users", tags=["Users"])
    # app.include_router(hospitals_router, prefix="/api/v1/hospitals", tags=["Hospitals"])
    # app.include_router(patients_router, prefix="/api/v1/patients", tags=["Patients"])
    # app.include_router(inventory_router, prefix="/api/v1/inventory", tags=["Inventory"])
    # app.include_router(beds_router, prefix="/api/v1/beds", tags=["Beds"])
    # app.include_router(doctors_router, prefix="/api/v1/doctors", tags=["Doctors"])
    # app.include_router(laboratory_router, prefix="/api/v1/laboratory", tags=["Laboratory"])
    # app.include_router(emergency_router, prefix="/api/v1/emergency", tags=["Emergency"])
    # app.include_router(analytics_router, prefix="/api/v1/analytics", tags=["Analytics"])
    # app.include_router(reports_router, prefix="/api/v1/reports", tags=["Reports"])
    # app.include_router(audit_router, prefix="/api/v1/audit", tags=["Audit"])

    # ── Health Check ───────────────────────────────────────────────────────────
    @app.get("/health", tags=["Health"])
    async def health() -> dict[str, str]:
        """Basic health check — confirms the API process is running."""
        return {"status": "healthy", "service": "hrip-backend"}

    @app.get("/ready", tags=["Health"])
    async def ready() -> dict[str, str]:
        """Readiness check — confirms DB and Redis are reachable."""
        # TODO Phase 1: check DB + Redis connectivity
        return {"status": "ready"}

    return app


app = create_app()
