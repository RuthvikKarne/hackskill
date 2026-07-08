"""Forecasting Service Router — Patient load and medicine demand forecasting."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query

from app.services.forecasting.service import ForecastingService
from app.schemas import ForecastResponse

router = APIRouter()
_service = ForecastingService()


@router.get(
    "/patient-load",
    response_model=ForecastResponse,
    summary="Forecast patient load",
    description=(
        "Forecast expected patient load for a hospital over the next N days. "
        "Uses EMA + day-of-week + monthly seasonality (Prophet-compatible output). "
        "Includes SHAP-style feature importance explanation."
    ),
)
async def forecast_patient_load(
    hospital_id: str = Query(..., description="Hospital UUID"),
    horizon_days: int = Query(7, ge=1, le=30, description="Forecast horizon in days"),
    base_daily_volume: float = Query(120.0, ge=1.0, description="Fallback baseline patients/day"),
) -> ForecastResponse:
    """Forecast expected patient load for the next N days."""
    return _service.forecast_patient_load(
        hospital_id=hospital_id,
        horizon_days=horizon_days,
        base_daily_volume=base_daily_volume,
    )


@router.get(
    "/medicine-demand",
    summary="Forecast medicine demand",
    description=(
        "Forecast 30-day medicine consumption for a hospital + medicine combination. "
        "Returns weekly breakdown, reorder point, and safety stock recommendation. "
        "Includes SHAP-style feature explanation."
    ),
)
async def forecast_medicine_demand(
    hospital_id: str = Query(..., description="Hospital UUID"),
    medicine_id: str = Query(..., description="Medicine identifier"),
    base_monthly_consumption: float = Query(500.0, ge=1.0, description="Fallback baseline units/month"),
) -> dict[str, Any]:
    """Forecast medicine consumption for the next 30 days."""
    return _service.forecast_medicine_demand(
        hospital_id=hospital_id,
        medicine_id=medicine_id,
        base_monthly_consumption=base_monthly_consumption,
    )
