"""Forecasting Service — Patient load and medicine demand forecasting.

Models (Phase 6):
  - Prophet + XGBoost for patient load prediction
  - Prophet for medicine demand forecasting

Input features:
  - Historical patient visit counts (per hospital)
  - Day of week, public holidays, festival calendar
  - Weather data (temperature, rainfall)
  - Historical disease pattern data
  - Current season / month

Output:
  - Expected patient count: next 7 days, next 30 days
  - Confidence interval
  - Forecast by department / ward
  - SHAP explanation of key drivers
"""
from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("/patient-load")
async def forecast_patient_load(hospital_id: str, horizon_days: int = 7) -> dict:
    """Forecast expected patient load for the next N days.

    TODO Phase 6: Implement with Prophet + XGBoost model.
    """
    return {
        "message": "Forecasting service — implementation pending (Phase 6)",
        "hospital_id": hospital_id,
        "horizon_days": horizon_days,
    }


@router.get("/medicine-demand")
async def forecast_medicine_demand(hospital_id: str, medicine_id: str) -> dict:
    """Forecast medicine consumption for the next 30 days.

    TODO Phase 6: Implement with Prophet model.
    """
    return {
        "message": "Medicine demand forecast — implementation pending (Phase 6)",
        "hospital_id": hospital_id,
        "medicine_id": medicine_id,
    }
