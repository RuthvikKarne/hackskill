"""HRIP AI Engine — FastAPI Application Entry Point.

This is a separate FastAPI service from the backend.

Responsibilities:
  - Demand forecasting (patient load, medicine)
  - Risk scoring per hospital
  - Resource optimization recommendations
  - Disease outbreak surveillance
  - Explainable AI (SHAP)

CRITICAL RULES:
  - AI Engine has READ-ONLY database access
  - AI Engine NEVER writes to any business table
  - AI Engine writes ONLY to analytics.ai_recommendations
  - All recommendations require human approval via the backend
  - AI Engine never executes actions autonomously
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

# Service routers (implemented in Phase 6)
from app.services.forecasting.router import router as forecasting_router
from app.services.optimization.router import router as optimization_router
from app.services.recommendation.router import router as recommendation_router
from app.services.risk_intelligence.router import router as risk_intelligence_router
from app.services.disease_surveillance.router import router as disease_surveillance_router
from app.services.explainability.router import router as explainability_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """AI Engine lifespan — model loading and cleanup."""
    # TODO Phase 6: Load trained models into memory
    # TODO Phase 6: Connect to read-only database
    # TODO Phase 6: Initialize feature store
    yield
    # TODO Phase 6: Release model resources


app = FastAPI(
    title="HRIP — AI Intelligence Gateway",
    description=(
        "AI recommendation engine for the Healthcare Resource Intelligence Platform. "
        "Provides demand forecasting, risk analysis, and resource optimization. "
        "All outputs are recommendations only — humans approve all actions."
    ),
    version="2.0.0",
    lifespan=lifespan,
)

# Mount service routers
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


@app.get("/health", tags=["Health"])
async def health() -> dict[str, str]:
    """AI engine health check."""
    return {"status": "healthy", "service": "hrip-ai-engine"}
