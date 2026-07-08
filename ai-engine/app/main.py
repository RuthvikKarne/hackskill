"""HRIP AI Engine — FastAPI Application Entry Point.

This is a separate FastAPI service from the backend.

Responsibilities:
  - Demand forecasting (patient load, medicine)
  - Risk scoring per hospital
  - Resource optimization recommendations
  - Disease outbreak surveillance
  - Explainable AI (SHAP)
  - Human approval workflow for all recommendations

CRITICAL RULES:
  - AI Engine has READ-ONLY database access
  - AI Engine NEVER writes to any business table
  - AI Engine writes ONLY to analytics.ai_recommendations
  - All recommendations require human approval via the backend
  - AI Engine never executes actions autonomously
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.feature_store import init_feature_store
from app.services.recommendation.service import init_recommendation_service

# Service routers
from app.services.forecasting.router import router as forecasting_router
from app.services.optimization.router import router as optimization_router
from app.services.recommendation.router import router as recommendation_router
from app.services.risk_intelligence.router import router as risk_intelligence_router
from app.services.disease_surveillance.router import router as disease_surveillance_router
from app.services.explainability.router import router as explainability_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """AI Engine lifespan — initialise feature store and recommendation service."""
    logger.info("HRIP AI Engine starting up...")

    # Initialise in-memory feature store
    feature_store = init_feature_store()
    logger.info("Feature store initialised: %s", feature_store.stats())

    # Initialise recommendation service (human approval workflow)
    recommendation_service = init_recommendation_service()
    logger.info("Recommendation service initialised.")

    logger.info("HRIP AI Engine ready — all services online.")
    yield

    logger.info("HRIP AI Engine shutting down.")


app = FastAPI(
    title="HRIP — AI Intelligence Gateway",
    description=(
        "AI recommendation engine for the Healthcare Resource Intelligence Platform. "
        "Provides demand forecasting, risk analysis, resource optimization, "
        "disease surveillance, and SHAP-based explainability. "
        "\n\n**All AI outputs are recommendations only — humans approve all actions.**\n\n"
        "## Services\n"
        "- `/api/v1/forecast` — Patient load and medicine demand forecasting\n"
        "- `/api/v1/risk` — Hospital risk scoring with SHAP explanations\n"
        "- `/api/v1/optimization` — Resource redistribution optimization\n"
        "- `/api/v1/surveillance` — Disease outbreak risk scoring\n"
        "- `/api/v1/explain` — SHAP explainability for any recommendation\n"
        "- `/api/v1/recommendation` — Human approval workflow\n"
    ),
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Mount service routers ─────────────────────────────────────────────────────
app.include_router(
    forecasting_router,
    prefix="/api/v1/forecast",
    tags=["Forecasting"],
)
app.include_router(
    optimization_router,
    prefix="/api/v1/optimization",
    tags=["Optimization"],
)
app.include_router(
    recommendation_router,
    prefix="/api/v1/recommendation",
    tags=["Recommendations"],
)
app.include_router(
    risk_intelligence_router,
    prefix="/api/v1/risk",
    tags=["Risk Intelligence"],
)
app.include_router(
    disease_surveillance_router,
    prefix="/api/v1/surveillance",
    tags=["Disease Surveillance"],
)
app.include_router(
    explainability_router,
    prefix="/api/v1/explain",
    tags=["Explainability"],
)


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/health", tags=["Health"])
async def health() -> dict[str, str]:
    """AI engine health check."""
    return {
        "status": "healthy",
        "service": "hrip-ai-engine",
        "version": "2.0.0",
        "services": "forecasting|risk|optimization|surveillance|explainability|recommendation",
    }


@app.get("/", tags=["Health"])
async def root() -> dict[str, str]:
    """AI engine root — redirect to docs."""
    return {
        "message": "HRIP AI Intelligence Gateway v2.0.0",
        "docs": "/docs",
        "health": "/health",
    }
