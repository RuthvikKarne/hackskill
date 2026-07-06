"""Disease surveillance service for MVP demo workflows."""
from __future__ import annotations

from fastapi import APIRouter, Query

from app.services.disease_surveillance.service import DiseaseSurveillanceService

router = APIRouter()
service = DiseaseSurveillanceService()


@router.get("/district-risk")
async def get_district_disease_risk(
    district_id: str,
    confirmed_cases: int = Query(0, ge=0),
    suspected_cases: int = Query(0, ge=0),
    new_cases_today: int = Query(0, ge=0),
    severity_score: float = Query(0.0, ge=0.0, le=1.0),
    weather_risk: float = Query(0.0, ge=0.0, le=1.0),
    population: int = Query(100000, ge=1),
) -> dict:
    """Return an explainable district disease-risk score for the MVP demo."""
    return service.analyze_district_risk(
        district_id=district_id,
        confirmed_cases=confirmed_cases,
        suspected_cases=suspected_cases,
        new_cases_today=new_cases_today,
        severity_score=severity_score,
        weather_risk=weather_risk,
        population=population,
    )
