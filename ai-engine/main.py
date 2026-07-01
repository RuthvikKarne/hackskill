from fastapi import FastAPI
from .services.forecasting.router import router as forecasting_router
from .services.optimization.router import router as optimization_router
from .services.recommendation.router import router as recommendation_router
from .services.risk_intelligence.router import router as risk_intelligence_router
from .services.disease_surveillance.router import router as disease_surveillance_router
from .services.explainability.router import router as explainability_router

app = FastAPI(
    title="Healthcare Intelligence Platform - AI Gateway",
    description="Central AI Engine for Predictions, Recommendations, and Optimizations.",
    version="1.0.0"
)

# Include routers
app.include_router(forecasting_router, prefix="/api/v1/forecast", tags=["Forecasting"])
app.include_router(optimization_router, prefix="/api/v1/optimization", tags=["Optimization"])
app.include_router(recommendation_router, prefix="/api/v1/recommendation", tags=["Recommendation"])
app.include_router(risk_intelligence_router, prefix="/api/v1/risk", tags=["Risk Intelligence"])
app.include_router(disease_surveillance_router, prefix="/api/v1/surveillance", tags=["Disease Surveillance"])
app.include_router(explainability_router, prefix="/api/v1/explain", tags=["Explainability"])

@app.get("/health")
def health_check():
    return {"status": "AI Gateway is running"}
