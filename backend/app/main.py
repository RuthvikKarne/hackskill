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

<<<<<<< HEAD
import redis.asyncio as aioredis
from fastapi import FastAPI
=======
from fastapi import Depends, FastAPI
>>>>>>> d9048f63f52a0d37227ef395a75b662abc01e5c8
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis

from app.config import get_settings
<<<<<<< HEAD
from app.core.database.session import close_db, init_db
from app.core.events.bus import get_event_bus, init_event_bus
from app.core.events.registry import event_registry
from app.core.exceptions.handlers import register_exception_handlers
from app.core.logging.logger import configure_logging, get_logger
from app.core.security.middleware import JWTAuthMiddleware
from app.middleware import RequestIDMiddleware
from app.modules.auth.router import router as auth_router
from app.modules.hospitals.router import router as hospitals_router

# ── Module routers will be imported here as they are implemented ──────────────
# from app.modules.auth.router import router as auth_router
# from app.modules.users.router import router as users_router
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
=======
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
>>>>>>> d9048f63f52a0d37227ef395a75b662abc01e5c8

# Module-level logger (configured before app creation)
log = get_logger(__name__)

# Redis client singleton — shared across request lifecycle
_redis_client: aioredis.Redis | None = None


def get_redis_client() -> aioredis.Redis:
    """Return the active Redis client.

    Raises:
        RuntimeError: If the application has not started yet.
    """
    if _redis_client is None:
        raise RuntimeError("Redis client is not initialised. Application has not started.")
    return _redis_client


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan — runs on startup and shutdown.

    Startup order (dependency-safe):
        1. Configure logging (first — everything else may log)
        2. Connect to PostgreSQL
        3. Connect to Redis
        4. Register event subscriptions
        5. Initialise Event Bus

    Shutdown order (reverse of startup):
        1. Drain Event Bus (in-process — no-op for now)
        2. Close Redis
        3. Close PostgreSQL
    """
<<<<<<< HEAD
    global _redis_client
    settings = get_settings()

    # ── 1. Logging ─────────────────────────────────────────────────────────────
    configure_logging(
        json_logs=settings.ENVIRONMENT == "production",
        log_level="DEBUG" if settings.DEBUG else "INFO",
    )
    log.info("hrip_backend_starting", version=settings.APP_VERSION, env=settings.ENVIRONMENT)
=======
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
>>>>>>> d9048f63f52a0d37227ef395a75b662abc01e5c8

    # ── 2. Database ────────────────────────────────────────────────────────────
    db_url = str(settings.DATABASE_URL).replace(
        "postgresql://", "postgresql+asyncpg://", 1
    )
    await init_db(
        database_url=db_url,
        pool_size=settings.DATABASE_POOL_SIZE,
        max_overflow=settings.DATABASE_MAX_OVERFLOW,
        echo=settings.DEBUG,
    )

    # ── 3. Redis ───────────────────────────────────────────────────────────────
    _redis_client = aioredis.from_url(
        str(settings.REDIS_URL),
        encoding="utf-8",
        decode_responses=True,
        max_connections=20,
    )
    await _redis_client.ping()
    log.info("redis_connected", url=str(settings.REDIS_URL))

    # ── 4. Event subscriptions ─────────────────────────────────────────────────
    # Register handlers here as modules are implemented (Phase 2+):
    # event_registry.subscribe("patients.patient.registered", audit_patient_registered)
    # event_registry.subscribe("inventory.medicine.stock_critical_low", notify_low_stock)
    # event_registry.subscribe("*", audit_all_events)  # wildcard for audit module
    log.info("event_subscriptions_registered", event_types=event_registry.registered_event_types)

    # ── 5. Event Bus ───────────────────────────────────────────────────────────
    init_event_bus(registry=event_registry)

    from app.core.database.session import get_session_factory
    from app.modules.hospitals.models import Hospital
    from sqlalchemy import select

    session_factory = get_session_factory()
    async with session_factory() as session:
        existing = await session.execute(select(Hospital).where(Hospital.deleted_at.is_(None)))
        if not existing.scalars().first():
            demo_hospitals = [
                Hospital(
                    name="Aster General Hospital",
                    code="AST-001",
                    type="district_hospital",
                    level="tertiary",
                    address="34 River Road",
                    city="Kigali",
                    state="Gasabo",
                    country="Rwanda",
                    phone="+250788123456",
                    email="info@astergeneral.example",
                    beds_capacity=240,
                    icu_beds=18,
                    status="active",
                    latitude=-1.9441,
                    longitude=30.0619,
                    description="District referral hospital with trauma and ICU services.",
                ),
                Hospital(
                    name="Cedar Community Clinic",
                    code="CED-002",
                    type="community_clinic",
                    level="primary",
                    address="12 Nyabugogo Avenue",
                    city="Kigali",
                    state="Nyarugenge",
                    country="Rwanda",
                    phone="+250788654321",
                    email="frontdesk@cedarclinic.example",
                    beds_capacity=72,
                    icu_beds=3,
                    status="active",
                    latitude=-1.9536,
                    longitude=30.0567,
                    description="High-volume community clinic supporting maternal and outpatient care.",
                ),
                Hospital(
                    name="Moringa Teaching Hospital",
                    code="MOR-003",
                    type="teaching_hospital",
                    level="tertiary",
                    address="88 Health Avenue",
                    city="Butare",
                    state="Huye",
                    country="Rwanda",
                    phone="+250783111222",
                    email="ops@moringa.example",
                    beds_capacity=320,
                    icu_beds=24,
                    status="operational",
                    latitude=-2.5958,
                    longitude=29.7399,
                    description="Teaching hospital serving the southern district network.",
                ),
            ]
            session.add_all(demo_hospitals)
            await session.commit()

    log.info("hrip_backend_ready")

    yield  # Application serves requests here

    # ── Shutdown ───────────────────────────────────────────────────────────────
<<<<<<< HEAD
    log.info("hrip_backend_stopping")

    await _redis_client.aclose()
    log.info("redis_disconnected")

    await close_db()
    log.info("hrip_backend_stopped")
=======
    from app.core.database.session import engine
    await engine.dispose()
    
    # TODO Phase 1: Close Redis
    # TODO Phase 1: Drain event bus
>>>>>>> d9048f63f52a0d37227ef395a75b662abc01e5c8


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

<<<<<<< HEAD
    # ── Exception handlers ─────────────────────────────────────────────────────
    # Registered before middleware so they catch middleware errors too
    register_exception_handlers(app)

    # ── Middleware (registered in reverse order — last added = first executed) ─
    # Order of execution for a request:
    #   RequestIDMiddleware → JWTAuthMiddleware → CORSMiddleware → Router
=======
    # ── Middleware ─────────────────────────────────────────────────────────────
    # Middlewares are executed bottom-up in Starlette.
>>>>>>> d9048f63f52a0d37227ef395a75b662abc01e5c8
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
        expose_headers=["X-Request-ID"],
    )
<<<<<<< HEAD
    app.add_middleware(
        JWTAuthMiddleware,
        public_key=settings.JWT_PUBLIC_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    app.add_middleware(RequestIDMiddleware)

    # ── Routers (uncomment as each module is implemented) ─────────────────────
    app.include_router(auth_router, prefix="/api/v1", tags=["Authentication"])
    # app.include_router(users_router, prefix="/api/v1/users", tags=["Users"])
    app.include_router(hospitals_router, prefix="/api/v1", tags=["Hospitals"])
    # app.include_router(patients_router, prefix="/api/v1/patients", tags=["Patients"])
    # app.include_router(inventory_router, prefix="/api/v1/inventory", tags=["Inventory"])
    # app.include_router(beds_router, prefix="/api/v1/beds", tags=["Beds"])
    # app.include_router(doctors_router, prefix="/api/v1/doctors", tags=["Doctors"])
    # app.include_router(laboratory_router, prefix="/api/v1/laboratory", tags=["Laboratory"])
    # app.include_router(emergency_router, prefix="/api/v1/emergency", tags=["Emergency"])
    # app.include_router(analytics_router, prefix="/api/v1/analytics", tags=["Analytics"])
    # app.include_router(reports_router, prefix="/api/v1/reports", tags=["Reports"])
    # app.include_router(audit_router, prefix="/api/v1/audit", tags=["Audit"])
=======
    
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
>>>>>>> d9048f63f52a0d37227ef395a75b662abc01e5c8

    # ── Health checks ──────────────────────────────────────────────────────────
    @app.get("/health", tags=["Health"])
    async def health() -> dict[str, str]:
        """Basic health check — confirms the API process is running."""
        return {"status": "healthy", "service": "hrip-backend"}

    @app.get("/ready", tags=["Health"])
<<<<<<< HEAD
    async def ready() -> dict[str, str | bool]:
        """Readiness check — confirms DB and Redis are reachable."""
        checks: dict[str, bool] = {"database": False, "redis": False}

        # Check PostgreSQL
        try:
            from app.core.database.session import get_engine
            from sqlalchemy import text
            async with get_engine().connect() as conn:
                await conn.execute(text("SELECT 1"))
            checks["database"] = True
        except Exception as exc:
            log.warning("readiness_db_failed", error=str(exc))

        # Check Redis
        try:
            await get_redis_client().ping()
            checks["redis"] = True
        except Exception as exc:
            log.warning("readiness_redis_failed", error=str(exc))

        all_ready = all(checks.values())
        return {"status": "ready" if all_ready else "degraded", **checks}
=======
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
>>>>>>> d9048f63f52a0d37227ef395a75b662abc01e5c8

    return app


app = create_app()
