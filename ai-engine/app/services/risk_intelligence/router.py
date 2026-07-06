"""Hospital risk intelligence service for MVP demo workflows."""
from __future__ import annotations

from fastapi import APIRouter, Query

from app.services.risk_intelligence.service import RiskIntelligenceService

router = APIRouter()
service = RiskIntelligenceService()


@router.get("/hospital-score")
async def get_hospital_risk_score(
    hospital_id: str,
    occupancy_rate: float = Query(0.0, ge=0.0, le=1.0),
    stock_shortage_ratio: float = Query(0.0, ge=0.0, le=1.0),
    average_wait_time: float = Query(0.0, ge=0.0),
    staff_shortage_ratio: float = Query(0.0, ge=0.0, le=1.0),
    severity_score: float = Query(0.0, ge=0.0, le=1.0),
) -> dict:
    """Return a hospital readiness and risk score for the MVP demo."""
    return service.assess_hospital_risk(
        hospital_id=hospital_id,
        occupancy_rate=occupancy_rate,
        stock_shortage_ratio=stock_shortage_ratio,
        average_wait_time=average_wait_time,
        staff_shortage_ratio=staff_shortage_ratio,
        severity_score=severity_score,
    )
