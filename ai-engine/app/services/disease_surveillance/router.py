"""Disease Surveillance Router — District outbreak risk scoring."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query

from app.services.disease_surveillance.service import DiseaseSurveillanceService

router = APIRouter()
_service = DiseaseSurveillanceService()


@router.get(
    "/district-risk",
    summary="Assess district disease outbreak risk",
    description=(
        "Compute a multi-feature outbreak risk score for a district. "
        "Uses incidence rate, case growth rate, clinical severity, weather risk, and CFR. "
        "Returns SHAP-style explanation and structured action alerts."
    ),
)
async def get_district_disease_risk(
    district_id: str = Query(..., description="District UUID"),
    confirmed_cases: int = Query(0, ge=0, description="Total confirmed cases"),
    suspected_cases: int = Query(0, ge=0, description="Total suspected cases"),
    new_cases_today: int = Query(0, ge=0, description="New cases reported today"),
    severity_score: float = Query(0.0, ge=0.0, le=1.0, description="Clinical severity index"),
    weather_risk: float = Query(0.0, ge=0.0, le=1.0, description="Environmental risk factor"),
    population: int = Query(100_000, ge=1, description="District population"),
) -> dict[str, Any]:
    """Return an explainable district disease-risk score."""
    return _service.analyze_district_risk(
        district_id=district_id,
        confirmed_cases=confirmed_cases,
        suspected_cases=suspected_cases,
        new_cases_today=new_cases_today,
        severity_score=severity_score,
        weather_risk=weather_risk,
        population=population,
    )
