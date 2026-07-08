"""Risk Intelligence Router — Hospital readiness and risk scoring."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query

from app.services.risk_intelligence.service import RiskIntelligenceService

router = APIRouter()
_service = RiskIntelligenceService()


@router.get(
    "/hospital-score",
    summary="Assess hospital risk score",
    description=(
        "Compute a composite hospital risk score using 5 weighted features. "
        "Returns risk level (low/moderate/high/critical), structured action recommendations, "
        "and a full SHAP-style feature importance explanation."
    ),
)
async def get_hospital_risk_score(
    hospital_id: str = Query(..., description="Hospital UUID"),
    occupancy_rate: float = Query(0.0, ge=0.0, le=1.0, description="Bed occupancy rate [0, 1]"),
    stock_shortage_ratio: float = Query(0.0, ge=0.0, le=1.0, description="Fraction of medicines below min stock [0, 1]"),
    average_wait_time: float = Query(0.0, ge=0.0, description="Average patient wait time in minutes"),
    staff_shortage_ratio: float = Query(0.0, ge=0.0, le=1.0, description="Fraction of unfilled staff positions [0, 1]"),
    severity_score: float = Query(0.0, ge=0.0, le=1.0, description="External severity index [0, 1]"),
) -> dict[str, Any]:
    """Return an explainable hospital readiness and risk score."""
    return _service.assess_hospital_risk(
        hospital_id=hospital_id,
        occupancy_rate=occupancy_rate,
        stock_shortage_ratio=stock_shortage_ratio,
        average_wait_time=average_wait_time,
        staff_shortage_ratio=staff_shortage_ratio,
        severity_score=severity_score,
    )
